# Authentication API

## Description

### What does it do?

Other applications can easily request api keys from discord users to authenticate them.

### How does it work?

The application sends a request to the bot, asking for the api keys for the specific user. The bot will then dm the user in question, asking which api keys he wants to share. 
The bot will then send the selected api keys to the other application.

If the user chooses not to choose any or does not respond, then the other application will be informed that the authentication process got canceled.

## Reference

### Sending the initial request

`GET` or `POST` request to `/requestapikey` with the following fields:

Field | Example | Description
-|-|-
`name`|`My super bot!`|The name of the application. Will be used to let the user know from which application the request was sent.
`userid`|`123456789012345678`|The discord user id.
`state`||**optional:** [XSRF](https://en.wikipedia.org/wiki/Cross-site_request_forgery) prevention. Can be anything and will be sent back to the callback without evaluation or modification.
`callback`|`https://example.com/callback`|The bot will call this url to deliver the api keys or to inform about a canceled authentication process.

The bot will answer with 200 `OK` on success or with an error message and the corresponding http code:

Error|Code|Description
-|-|-
`invalid method call <type>`|400|The request was no `GET` or `POST` request.
`missing parameters`|400|The request did not include all required fields.

### Receiving an answer

The bot will make a post request to the callback with the following fields:

Field|When|Description
-|-|-
`userid`|everytime|The discord user id
`state`|everytime|The csrf flag
`api_keys`|on success|An array with all api keys the user chose to share
`error`|on error|The error message

#### Possible errors:

Error|Description
-|-
`user canceled`|The user entered an invalid response.
`timeout`|The user did not respond in time.
`user blocked verification dm`|The user does not allow the bot to message him.