## Wozzit Message Object Reference

* Version: 0.1.1
* Protocol: 0.0.1
* Platform: Python

#### Requirements

* Python 2.7.x

#### External Dependancies

* requests `pip install requests`

#### Installation

```python
pip install wozzit
```

#### Creating an Instance

```python
import wozzit

msg = wozzit.Message([json])
```

* **json** : A Python dictionary representing a serialised Message. if provided, this will be read in and parsed. See _loads()_ for more details.


### Properties

#### Message.protocol

_Array_ **Default: [0, 0, 1]**

A three-element array representing the Wozzit protocol version in semantic versioning format (symver). The current protocol version is 0.0.1 so the content of Message.protocol is [0, 0, 1] by default.

The protocol is used by the server to determine whether it can process the message. This will allow for changes in the Wozzit Message specification in future.

The object has internal values that determine what version of message it can support, so may reject a message when deserialising if the protocol given is not supported.

#### Message.schema

_String_ **Default: "wozzit.null"**

A string in reverse-DNS notation determining what the message contains. It is expected that you use your own domain/identity as the prefix to any types of schemas you create. This is to try and avoid collisions where we have multiple type of messages sharing the same schema name. So, if you have 'example.org' then prefix all your schema names with 'org.example.'. the only exception is the prefix 'wozzit.' which is reserved for system use.

* Bad schema names: 'test', 'rain', 'my_super_schema', 'wozzit._anything_'
* Good schema names: 'org.mydomain.lightsaber', 'com.weather.alerts'

#### Message.version

_Int_ **Default: 1**

As schemas can change, _version_ is provided to specify which version of the schema is being implemented in the message. The header is mandatory but it's up to you how you use it so long as it remains an integer.

#### Message.ip

_String_

Only populated in received messages. This property is set by the receiving server so you check from where the message was sent. This is to allow filtering by IP address if required.

#### Message.psk

_String_

A pre-shared key. You can add security to your messages by ensuring each device transmits the PSK with their messages. You can then add it as a match requirement for incoming messages. There are no constraints on what is contained.

#### Message.payload

_Variant_

The actual content of the message. The content, whether it be a number, string or dictionary, is determined by the rules laid down in the schema. If a schema states that the payload content is either a simple True or False, it is reasonable for you to only check for that. There's no reason why a payload couldn't contain much more complex information such as nested database records or encoded binary data.

### Methods

#### Message.toDict()

Returns the message serialised into a Python dictionary

#### Message.toJSON()

Returns the message serialised into JavaScript object notation.

#### Message.loads(_data_, [_ip_])

Deserialise either a Python Dictionary or JSON message into the object. Returns either an 'wozzit.error' message object or True. The _ip_ argument is for server use.

#### Message.send(_to_)

Not using a server instance? This shortcut allows you to send the current message to another server. _to_ must be the full URL including port. Returns a _requests_ response object.

### Examples

Create a Wozzit Message and send it to a server.

```python
import wozzit

msg = wozzit.Message()
msg.schema = "com.mydomainname.colours"
msg.payload = "green"
msg.send("http://192.168.0.2:10207/")
```

Receive a message and parse it

```python
import wozzit

def incoming(json):
	msg = wozzit.Message(json)
	if msg.schema == "com.mydomainname.colours"
		print "Today's colour is " + msg.payload
```

A more complicated payload and server

```python
import wozzit

msg = wozzit.Message()
svr = wozzit.Server()

msg.schema = "com.mydomainname.user"
msg.payload = {
	"username": "john",
	"firstName": "John",
	"secondName": "Doe"
}

svr.send(msg, "http://192.168.0.2:10207/")
```

