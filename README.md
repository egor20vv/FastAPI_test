# FastAPI_test

Implements a simple REST user management service

## Run

To run application use the next command:

```bash
python main.py
```

## Usage

Firstly, open the page http://127.0.0.1:5000/

Then you can manage users with routing:

### GET requests

```url
http://127.0.0.1:5000/users[?skip=(number, default=0)&limit=(number, default=100)]
```
This will return full data about users in noted limits

```url
http://127.0.0.1:5000/users/count
```
Returns count of users

```url
http://127.0.0.1:5000/users/(user identifier: id or nick name)
```
Returns whole data about concrete user
 
### POST requests
 
URL:
```url
http://127.0.0.1:5000/users
```

Data format: 
```JSON
{
  "nik_name": "string",
  "fst_name": "string",
  "sec_name": "string"
}
```
This will create a user or report a error

### PUT requests

URL:
```url
 http://127.0.0.1:5000/users/(user identifier: id or nick name)
```

Data format:
```JSON
{
  "nik_name": "string",
  "fst_name": "string",
  "sec_name": "string",
  "status": 0
}
```
This will update a concrete user.

<i>Please note that none of the above data fields are important, that is, they can be neglected.</i>

### DELETE request

```url
 http://127.0.0.1:5000/users/(user identifier: id or nick name)
```
This will delete a concrete user.


 
