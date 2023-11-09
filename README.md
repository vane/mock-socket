mock-socket
====
Proof of concept.  

Record and replay socket traffic to mock socket connection  

## working example  

### record

1. start mysql server on `127.0.0.1:3306`
2. start `record.py` to record traffic
3. connect to `record.py` on `127.0.0.1:3307` by using `test/test-mysql.py`
4. `record.py` capture and proxy all traffic from `127.0.0.1:3307` to `127.0.0.1:3306`
5. each time after client socket is closed `record.py` dumps traffic to `dump.bin` (override file)
6. stop `record.py`

Traffic is recorded, and we can replay it using same flow but instead of 
`record.py` we use `replay.py`.

We don't need mysql server this time - `replay.py` receive traffic 
from `test/test-mysql.py` and replies with traffic from `dump.bin` 

### replay
1. start `replay.py` to replay traffic
2. `replay.py` reads `dump.bin`
3. connect to `replay.py` on `127.0.0.1:3307` by using `test/test-mysql.py`
4. traffic is replied - no exception is thrown
5. stop `replay.py`

### TODO
- add ability to specify configuration file
- test on different sockets instead of only mysql socket
