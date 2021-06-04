DBlink
======
Download Blinks of the day.

Install
-------
Run `pip -r requirements.txt`.

Run
---
```
mkdir out
python dblink.py
```


Docker
------
Build an image with `docker build -t dblink` and run a container:
`docker run -v /var/www/blinks/:/code/out --rm dblink`.
 
