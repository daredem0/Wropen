# Wropen - A minimalistic subprocess.Popen interceptor

## Usage
Before the decorator can be used the inner state of the 
Wropen has to be configured at least once. The state is persistent over all instances. If the debug flag is set, subprocess.Popen calls will be intercepted.
If not, subprocess.Popen will be called directly. The flag can be 
changed during execution.
```python
@Wropen.intercept_popen
def a_function_that_calls_popen():
    ...

def some_function():
    wropen_state = WropenState(
        WropenMode.PASS, WROPEN_PASS_PATH
    )
    wropen_state.debug = True
    Wropen.configure(wropen_state)
    a_function_that_calls_popen()

```
The wrapper will pretend to be a typical Popen call and reply 
on stdout and stderr with either a defined answer, or the stdin if no answer is defined. Replys can be defined in a simple json format.
```json
{
    "message_0":{
        "message": "ls",
        "reply": "ls dummy reply"
    },
    "message_1":{
        "message": "ls -lh",
        "reply": "ls -lh dummy reply",
        "error": "no such command"
    }
}
```
The returncode property is set to **0** if Wropen mode is *PASS* and **1** if the Wropen mode is *FAIL*.
