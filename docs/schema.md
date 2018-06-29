## Wozzit Message Schema

### Protocol Version 0.0.1

I’ll be honest, I’m not much good at this technical authoring lark. Apologies if this is a little, err, _informal_. My main is to keep this documentation as simple and plain as possible, so don’t expect an RFC.

Wozzit servers exchange messages. The whole key to Wozzit is making sure those messages adhere to a few simple rules that are outlined here.

Wozzit does not dictate what protocol or markup language is used for a message so long as its content follows the (very simple) schema. Here we’ll be using JSON primarily but you can represent Wozzit messages in just about anything.

### The Wozzit Container

Whatever format the message takes, it must be nested inside a container called ‘wozzit’. Why? So if you want to send the message along with other information, you can without breaking any rules.

In JSON it looks like this:

```json
{
    "wozzit": {
    	...
    }
}

```

In YAML it would look like this:

```yaml
wozzit:
    ...
```
In XML:

```xml
<whatever>
	<wozzit>
		...
	</wozzit>
</whatever>
```

Why 'whatever'? Because anything claiming to be Wozzit compliant should not care what the document root node is named, just that there is a child called 'wozzit'.

### The Envelope

What now follows is the 'envelope', some metadata that tells us what the main part of the message will contain. As we are dealing with different markups, I'll refer to these of 'key-pairs', that is, a unique key and corresponding value.

#### Mandatory Key-Pairs

The following key-pairs must exist in a Wozzit message to be considered valid (order is unimportant):

**protocol**

The version number of the Wozzit message. To allow for future changes, this is required. The version number is expressed using semantic versioning ('symver'), composed of a major, minor and revision number expressed as an array. At time of writing the current (and only) protocol version is 0.0.1. In a Wozzit message this is expressed as an array: (0, 0, 1).

JSON Example

```json
{
	"wozzit": {
		"protocol": [0, 0, 1]
	}	
}
```

YAML Example

```yaml
wozzit:
	protocol: 
	- 0
	- 0
	- 1
```
This gives the server a fighting chance of deciding whether it can support the incoming message or not and responding accordingly.

**schema**

Schema is a string that describes what content is contained in the message. Schemas are described in reverse domain name notation (reverse-DNS). Although unenforceable, the intention is that all schemas are unique to avoid confusion.

Let's say that you own example.com and have dreamt up a schema for controlling your toaster and you want to call it 'toaster'. The correct schema name would be 'com.example.toaster'. You can add whatever you like after the 'com.example' part as it's yours. If you want 'com.example.my.amazing.cool.thing.version.1.final.FINAL.2' you can (but please don't).

The only exception is 'wozzit.*'. Any schema starting _wozzit._ should be considered reserved for system use. There are a number of built-in messages what use the _wozzit._ namespace.

**version**

Things can change, so the final mandatory key-pair in the envelope is a version for the schema. This is a simple single integer number which, if you want to keep your schema name but change it's rules, can be incremented. Default is '1'.

JSON Example

```json
{
	"wozzit": {
		"protocol": [0, 0, 1],
		"schema": "com.example.toaster",
		"version": 1
	}	
}
```

YAML Example

```yaml
wozzit:
	protocol: 
	- 0
	- 0
	- 1
	schema: 'com.example.toaster'
	version: 1
```

**payload**

Here's the good bit. The payload is the main content of the message and contains whatever your schema dictates. There are no rules here except what the schema states should be present.

Example: You have a schema called com.example.cheese. The schema states that the payload with contain one single key-pair called 'cheese' with a string which is the name of a nice cheese.

Here it is in JSON format:

```json
{
	"wozzit": {
		"protocol": [0, 0, 1],
		"schema": "com.example.cheese",
		"version": 1,
		"payload": {
			"cheese": "Cheddar"
		}
	}
}
```

#### Optional Key-Pairs

The following are envelope key-pairs that are optional, so server implementations should not rely on them.

**psk**

We all need some security in our lives, so psk adds some for Wozzit. Short for 'Pre-Shared Key', this field exists to allow messages to contain passwords. A receiving server can check the contents of this field (which can be anything you like, even an object) before accepting the message and processing it.

**ip**

It is acceptable for a server implementation to add a header called 'ip' that contain the IPv4 address of the client. This can be used to filter messages by origin. It should never be set by the client themselves.

**x-\***

If you would like to include customer headers in the envelope, you are welcome to do so as long as you accept that servers are not obliged to recognise them. All customer headers should start with **x-\***.

#### Examples

Here is a fully-compliant Wozzit message

```json
{
	"wozzit": {
		"protocol": [0, 0, 1],
		"schema": "com.example.temperatures",
		"version": 1,
		"psk": "hs6skfb",
		"payload": {
			"unit": "celsius",
			"internal": 20,
			"external": 27.6,
			"jupiter": -145
		}
	}
}
```

Although the payload is a required key, it is not mandatory for it to have any content:

```json
{
	"wozzit": {
		"protocol": [0, 0, 1],
		"schema": "com.example.ping",
		"version": 1,
		"payload": null
	}
}
```
A more complicated example:

```json
{
	"wozzit": {
		"protocol": [0, 0, 1],
		"schema": "com.example.profile",
		"version": 1,
		"psk": "7DSFJKjhjhgcnwo3tfscjn6skSb",
		"x-server": "server1.example.com",
		"x-username": "user1",
		"payload": {
			"name": "User 1",
			"email": "user1@example.com",
			"address": {
				"line1": "61 Acacia Road",
				"line2": "Anywhere",
				"country": "United Kingdom",
				"postalCode": "ABC 123"
			},
			"avatar": "N8uqlUa1rb09da75XGW7JGBV2aHRMAIECBAgQIAAAQIECBAgUA2Bjy5I6W2zU7ry1yn9aofAVTVGZeytiGDV9OXL0vkfWzn2Qsb5lR3jXL7iCRAgQIAAAQIECBAgQIAAgRYQ+M7SlO57NqXvPpnStX9I6eiJFuhUzboQOatiGWDMrKpysCqGRcCqZv84dZcAAQIECBAgQIAAAQIECIxVIGZaxWOyHku690/Wpteu3ZYE1m7IdZgAAQIECBAgQIAAAQIECBAgUG0BAatqj4/WESBAgAABAgQIECBAgAABAgRqJyBgVbsh12ECBAgQIECAAAECBAgQIECAQLUFBKyqPT5aR4AAAQIECBAgQIAAAQIECBConYCAVe2GXIcJECBAgAABAgQIECBAgAABAtUWELCq9vhoHQECBAgQIECAAAECBAgQIEBgUgic7OkprZ0CVqVRKogAAQIECBAgQIAAAQIECBAgUF+BI0eOldb5UgNWPSfKi6SV1kMFESBAgAABAgQIECBAgAABAgQIjKtAxIT27u8urY5SA1Y79x5Ihw91pzKngJXWUwURIECAAAECBAgQIECAAAECBAiUKhAxoIgFRUzoRM/J0sruKK2kXNDeV81Je8ssUFkECBAgQIAAAQIECBAgQIAAAQK1E2jbvqurvPBX7fh0mAABAgQIECBAgAABAgQIECBAoGyBUpcElt045REgQIAAAQIECBAgQIAAAQIECNRPQMCqfmOuxwQIECBAgAABAgQIECBAgACBSgsIWFV6eDSOAAECBAgQIECAAAECBAgQIFA/AQGr+o25HhMgQIAAAQIECBAgQIAAAQIEKi0gYFXp4dE4AgQIECBAgAABAgQIECBAgED9BASs6jfmekyAAAECBAgQIECAAAECBAgQqLSAgFWlh0fjCBAgQIAAAQIECBAgQIAAAQL1ExCwqt+Y6zEBAgQIECBAgAABAgQIECBAoNIC/wMhKDayMNVrTAAAAABJRU5ErkJggg=="
		}
	}
}
```
