# Gitreview
Make PRs faster! Make PRs better?

## Installation
1. Clone the [repo](https://hq-stash.elementalad.com/users/briauron/repos/bauron-sandbox/browse)
1. `cd bauron-sandbox/python3/gitreview`
1. `python setup.py install`

## Setup
1. `gitreview --configure` and answer the prompts
_OR_
1. Create your own file as in `caveats` below, satisfying the yaml format:
```
---
stashuser: stashusername #required
stashpass: stashpassword #required
proxy: 127.0.0.1:9000    #optional
proxyuser: proxyusername #optional
proxypass: proxypassword #optional
```

## Use
1. Make a git branch, edit stuff, make a commit!
1. `gitreview`

## Caveats
1. Requires `~/.stashcreds.yaml` containing at a minimum:
```
---
stashuser: butts
stashpass: lol
```

## TODO
Make this README less shitty.
Make this library less shitty.
