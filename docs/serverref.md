## Wozzit Server Reference

* Version: 0.1.1
* Protocol: 0.0.1
* Platform: Python
* Protocol: HTTP

#### Requirements

* Python 2.7.x

#### External Dependancies

* requests `pip install requests`
* Notification library (optional) see desktopNotification() method below

#### Creating an Instance

```python
import wozzit

svr = wozzit.Server(opts)
```

### Server.listen([_opts_])

Start the server and await connections.

`opts` = Dictionary of options as follows. All are optional.

Key|Values
---|------
ip|IPv4 Address on which to listen. Omit to listen on all.
port|Port on which to listen. Default is 10207.
smtp.host|SMTP host for sending email
smtp.port|SMTP server port
smtp.SSL|Demand SSL connection? True/False
smtp.username|If required, authentication username
smtp.password|If required, authentication password
smtp.fromName|Friendly name of originator
smtp.fromEmail|Email address of originator
onError|Callback to be called if a trappable error occurs

#### Server.setOptions(_opts_)

Sets the server options as detailed in _listen()_ but does not start the server.

#### Server.send(_msg_, _to_)

Send a message to another Wozzit node.

Argument|Description
--------|-----------
msg|A Wozzit Message instance
to|The full URL to to send to

A Wozzit server will issue a message which is returned by this method if the transmission was received. A message of schema 'wozzit.receipt' can be considered successful. If the schema is 'wozzit.error', the payload should be inspected to discover the problem.

##### Example

```python
import wozzit

svr = wozzit.Server()
msg = wozzit.Message()
msg.schema = "wozzit.test"
response = svr.send(msg, "http://192.168.0.2:10207/")
print(response.schema)
```

### Listener Methods

The following methods add 'hooks' that are called when a message is received. Each method takes a _match_ argument which determines whether that hook is processed against the received message.

_match_ is a dictionary that echoes items in the message envelope.

Listener methods have no return values.

#### Examples

```python
match = {
	"schema": "wozzit.rain"
}
```

The listener will only be called for messages that have the schema 'wozzit.rain'.

```python
match = {
	"schema": "wozzit.rain",
	"psk": "jskdq87rehfyg837ofnj"
}
```

For added security, this will only run if the schema is 'wozzit.rain' and the correct pre-shared key has been provided.

```python
match = {
	"schema": "wozzit.rain",
	"psk": "jskdq87rehfyg837ofnj",
	"ip": "192.168.0.1"
}
```

Same again, but not the IPv4 address must match as well (this header is set by the receiving node, not by the client).

You are free to add your own arbitary headers provided they are prefixed with 'x-'. If match is omitted, all messages match.


#### Server.addLog([_match_])

Print the message contents to the console whenever a message matches the criteria in _match_.

#### Server.addListener([_match_], _callback_)

Where callback is a defined function. The function is called if the message is matched. This allows you to run your own code when a message is received, so you can do whatever you like.

The called function is passed the match dictionary and the full message instance for processing.

##### Example

```python
import wozzit

def myFunction(match, message):
	-- Do exciting stuff here--

svr = wozzit.Server()
svr.addListener({"schema": "wozzit.test"}, myFunction)
svr.listen()
```

Now myFunction will be called whenever a message of schema 'wozzit.test' is received.

#### Server.addForwarder([_match_], _to_)

Automatically forward any matched message to another server. 'to' must contain the full URL including port.

##### Example

```python
import wozzit

svr = wozzit.Server()
svr.addListener({"schema": "wozzit.test"}, "http://192.168.0.2:10207/")
svr.listen()
```

This is a 'best efforts' attempt with no queuing or retries. If you need to ensure the message is sent, you can implement your own system using addListener().

#### Server.addDesktopNotification([_match_], _message_)

Display a simple notification the recipient's desktop. Uses different libraries to support Linux, Mac and Windows. If a message is matched, the contents of _message_ are displayed as a pop-up notification. Great for testing, but more complicated messages can be created using addListener() and your own functions.

#### Server.addDesktopNotification([_match_], _toName_, _toEmail_, _subject_, _message_)

If a message is matched, send a simple email.

Argument|Description
--------|-----------
toName|The friendly name of the recipient
toEmail|The email address of the recipient
subject|The subject line for the email
message|The body content of the email

For this function to work, SMTP options must have been set using listen() or setOptions(). If not, the event is ignored.

For more complicated requirements, you can implement your own callback using addListener() with the helper method _sendEmail()_.

#### Server.sendEmail(_toName_, _toEmail_, _subject_, _body_)

As sending emails is a common task in the Wozzit world, this internal method is exposed for the implementer's convenience. If you wish, you can include this call in your callback methods to allow you to inspect the contents of a message and customise your response accordingly.

Argument|Description
--------|-----------
toName|The friendly name of the recipient
toEmail|The email address of the recipient
subject|The subject line for the email
message|The body content of the email

For this function to work, SMTP options must have been set using listen() or setOptions(). If not, the event is ignored.

Returns True or False depending on whether the message was successfully sent.

#### Server.desktopNotification(_title_, _message_)

Display an on-screen notification. This is used by the _addDesktopNotification_ listener, but can also be used by your own callbacks, so you customise the notification based on the received message.

Argument|Description
--------|-----------
title|The main heading of the message 
message|The notification content

This method uses the following libraries per platform:

Library|Platform
-------|--------
pync|macOS
toaster|Windows
notify2|Linux Desktop

The appropriate library will need to be installed for notifications to work.