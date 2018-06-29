## Wozzit Server

### Protocol Version 0.0.1

Wozzit does not prescribe any particular type of server. If you want to use MQTT, semaphone or carrier pigeons to relay messages please feel free to do so. Realistically, we need something commonly used in place, so the Wozzit implementations found on the GitHub repository provide an implementation in HTTP for your use. This document describes its usage.

#### Python
The Python library is the simplest to use. To create a Wozzit server, here is all the code you need:

```python
import wozzit

svr = wozzit.Server()
svr.listen()
```

This will create a HTTP Wozzit 'node' listening on port 10207 and sit there waiting for connections. However, as no rules have been specified, the server won't actually do anything when a message has been received.

Adding 'listeners' allows the server to react to any incoming messages. There are two parts to adding a listener: What criteria to match against the incoming message and what to do if a match is made.

This server implementation provides a number of listeners built-in but the most commonly used is the generic listener. Here a callback is used so you can add your own code to react to the incoming message.

```python
import wozzit

def printCheese(match, msg):
	print msg.payload.cheese + " is a nice cheese"
	
svr = wozzit.Server()
svr.addListener({"schema": "wozzit.cheese"}, printCheese)
svr.listen()

```

Here we've defined a function call 'printCheese' and then added a listener to call printCheese if a message arrives with the schema of 'wozzit.cheese'. It will not be called for any other type of message.

The 'callback' function is passed two arguments, the matching criteria that was used and the message received (both dictionaries in Python parlance). Generally you'll be interested in msg.payload as that will contain the information provided by the message.

You can add as many listeners as you like, and run what code you like as a result. Matching parts of the envelope is fairly rigid at this time, but that'll be improved to support things like regular expressions.

Another important feature of the server implementation is the ability to forward messages from one server to another. Let's say you have a rain detector that can send a message of schema 'wozzit.rain' to let you know it's raining. You have a laptop so it may or may not have its Wozzit server running. So, you have a server running at home and configure the rain detector to it always sends a message to the server. The server is then configured to do two jobs: Send an email to a notification gateway such as Pushover and then relay the message to the laptop. If the laptop server is offline (i.e. the laptop is on its travels), the notification email is still processed. Here's how that's implemented:

```python
import wozzit

svr = wozzit.Server()
svr.addEmail({"schema": "wozzit.rain"}, "John Doe", "john@doe.com", "Rain alert", "It's raining dude!");
svr.addForwarder({"schema": "wozzit.rain"}, "http://laptop.local:10207/")
svr.listen()
```

Two built-in listeners have been added. The first is a simple email sender that matches again a schema of 'wozzit.rain' and emails John Doe with a simple message. If you need something with custom fields you can add a callback to construct a more complicated message.

The second listener forwards any matching messages to another server, in this case 'laptop.local'. The implementation is fairly laid-back and will make 'best efforts' to send the message. It won't queue or retry (yet).

On the laptop:

```python
import wozzit

svr = wozzit.Server()
svr.addDesktopNotification({"schema": "wozzit.rain"}, "It's raining dude!");
svr.listen()
```

Here the built-in 'addDesktopNotification' listener will pop up a desktop alert when the message is received.

#### Some Security

We can add some security by using **ip** and **psk** headers. This server implementation adds the envelope header **ip** to the message upon receipt. That way we know where it came from. So, if we wanted we could add IP filtering to our laptop like so:

```python
svr.addDesktopNotification({
	"schema": "wozzit.rain",
	"ip": "192.168.0.2"
	}, "It's raining dude!");
```

Now, if the message did not come from 192.168.0.2, it is discarded.

Additionally, all the message can have a pre-shared key (PSK) set that is known only to them.

```python
svr.addDesktopNotification({
	"schema": "wozzit.rain",
	"ip": "192.168.0.2",
	"psk": "klufihyti7qyru6tr"
	}, "It's raining dude!");
```

If the incoming message does not contain the correct PSK, it is rejected.

Full Server Implementation Reference
