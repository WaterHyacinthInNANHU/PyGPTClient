# PyGPTClient

This is a python client for [node-gpt-api](https://github.com/waylaidwanderer/node-chatgpt-api). (Only supports BingAI by now; welcome for PR!)

## Quick Install

1. Python 3.7+ is required.

	To render the querying resutls with `render.py`, install `markdowngenerator` using pip:

	```
	pip3 install git+https://github.com/Nicceboy/python-markdown-generator
	```
2. Install [node-gpt-api](https://github.com/waylaidwanderer/node-chatgpt-api) following [official instructions](https://github.com/waylaidwanderer/node-chatgpt-api#getting-started)

## Example Usage

1. Config API server in `gpt_api/settings.js`. Set `userToken`/`cookies` and `proxy`(if necessary). Tips: visit `edge://settings/siteData?search=cookie` in Edge for cookie.
   ```js
       bingAiClient: {
        ...
        // The "_U" cookie value from bing.com
        userToken: '',
        // If the above doesn't work, provide all your cookies as a string instead
        cookies: '',
        // A proxy string like "http://<ip>:<port>"
        proxy: '',
		...
    },
   ```
2. Luanch API server: 
   ```bash
   cd gpt_api
   chatgpt-api
   ```

3. Edit your questions in `gpt_client.py`. Responds will be saved to `results` as json.

	```python
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
	```
	```bash
	python gpt_client.py
	```
4. (Optinal) Render the responds as `results.md`
   ```bash
   python render.py
   ```

## TODO
 - [x] Support BingAI
 - [ ] Support ChatGPT