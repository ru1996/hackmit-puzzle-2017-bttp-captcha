# hackmit-puzzle-2017-bttp-captcha
Help Marty McFly return to the current year.

## Use from scratch
```bash
docker build . -t hackmit-puzzle-2017-bttp-captcha
docker run -p 8125:8125 -p 8126:8126 --name statsd -d dockerana/statsd
docker run -d -p 8081:8000 -e STATSD_HOST=localhost hackmit-puzzle-2017-bttp-captcha
```