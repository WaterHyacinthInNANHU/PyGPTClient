import requests, json, time, random
from typing import List
import os.path as osp
import os
from dataclasses import dataclass, asdict


@dataclass
class Host:
	host: str = '127.0.0.1'
	port: int = 3000

	def conversation_url(self) -> str:
		return f"http://{self.host}:{self.port}/conversation"

	def new_session_url(self) -> str:
		return f"http://{self.host}:{self.port}/turing/conversation/create"


@dataclass
class Session:
	message: str = "Hello, how are you today?"
	toneStyle: str = "precise"
	conversationId: str = ''
	conversationSignature: str = ''
	clientId: str = ''
	invocationId: str = ''

	def data_for_first_query(self) -> dict:
		res = asdict(self)
		for key in ['conversationId', 'conversationSignature', 'clientId', 'invocationId']:
			res.pop(key)
		return res

	def data(self) -> dict:
		return asdict(self)

	def set_context(self, context: dict) -> None:
		self.conversationId = context['conversationId']
		self.conversationSignature = context['conversationSignature']
		self.clientId = context['clientId']
		self.invocationId = context['invocationId']

	def set_question(self, question: str) -> None:
		self.message = question


class BingAIClient():
	def __init__(self, 
				host='127.0.0.1', port: int = 3000,	
				pacing_between_questions_ms: int = 2000,	
				pacing_between_questions_var_ms: int = 1000,	
				pacing_between_sessions_ms: int = 5000,
				toneStyle: str = "precise",
				verbose: bool = False
			) -> None:
		"""
		Args:
			host (str): host of the server
			port (int): port of the server
			pacing_between_questions_ms (int): pacing between questions in milliseconds
			pacing_between_questions_var_ms (int): variance of pacing between questions in milliseconds
			pacing_between_sessions_ms (int): pacing between sessions in milliseconds
			toneStyle (str): tone style, can be balanced, creative, precise and fast, see https://github.com/waylaidwanderer/node-chatgpt-api/blob/main/demos/use-bing-client.js for details
		"""
		self.host = Host(host, port)
		self.sess = Session(toneStyle=toneStyle)
		self.pacing_between_questions_ms = pacing_between_questions_ms
		self.pacing_between_questions_var_ms = pacing_between_questions_var_ms
		self.pacing_between_sessions_ms = pacing_between_sessions_ms
		self.verbose = verbose
		self.sess_num = 0
		self.quest_num = 0

	def _ask(self, q: str) -> requests.Response:
		self.sess.set_question(q)
		res = None
		# https://github.com/waylaidwanderer/node-chatgpt-api/pull/453 timing out may happen in peak hours
		while res is None or (res.status_code != 200 and 'Timed out waiting for response.' in res.text): 
			is_first = self.quest_num == 0
			if is_first:
				self._log(self.sess.data_for_first_query())
				res = requests.post(self.host.conversation_url(), json = self.sess.data_for_first_query())
			else:
				self._log(self.sess.data())
				res = requests.post(self.host.conversation_url(), json = self.sess.data())
		self.quest_num += 1
		return res

	def _save_results(self, path, res) -> None:
		# save results to json
		os.makedirs(osp.dirname(path), exist_ok=True)
		with open(path, 'w') as f:
			json.dump(res.json(), f, indent=4)

	def _log(self, msg: str) -> None:
		if self.verbose:
			print(msg)

	def new_session(self) -> requests.Response:
		res = requests.get(self.host.new_session_url())
		self._log(f"Sleeping for {self.pacing_between_sessions_ms / 1000} seconds between sessions...")
		time.sleep(self.pacing_between_sessions_ms / 1000)
		self.sess_num += 1
		return res

	def ask_questions(self, questions: List[dict]) -> List[requests.Response]:
		results = []
		for idx, question in enumerate(questions):
			q = question['q']
			self._log(f"Asking question {idx + 1}: {q}...")
			res = self._ask(q)
			# warn if the response is not 200
			if res.status_code != 200:
				raise RuntimeError (f"Warning: error code {res.status_code} Error message: {res.text}")
			else:
				self._log(f"Success")
			if idx == 0: # set context after the first request
				self.sess.set_context(res.json())
			sleep_for = max(( self.pacing_between_questions_ms + random.randrange(-self.pacing_between_questions_var_ms, self.pacing_between_questions_var_ms) ) / 1000, 0)
			self._log(f"Sleeping for {sleep_for} seconds between questions...")
			time.sleep(sleep_for)
			results.append(res)
			# save results to json
			if 'save_as' in question.keys():
				self._save_results(question['save_as'], res)
		return results


if __name__ == '__main__':
	# example usage
	questions_with_saving = \
		[
			{'q': "How is the air quality in NYC in 2023? Please provide some references.", # one question
			'save_as': 'results/001_nyc.json'},
			{'q': 'What about Boston?',
			'save_as': 'results/002_boston.json'},
		]

	questions_without_saving = \
		[
			{'q': "How is the air quality in NYC in 2023? Please provide some references."}, # one question,
			{'q': 'What about Boston?'},
		]

	client = BingAIClient(host='127.0.0.1', port=3000, verbose=True, pacing_between_sessions_ms=2000)
	client.new_session()
	client.ask_questions(questions_with_saving)
	client.new_session()
	client.ask_questions(questions_without_saving)
