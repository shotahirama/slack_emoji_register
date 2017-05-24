# slack_emoji_register

## INSTALL
```
git clone https://github.com/shotahirama/slack_emoji_register.git
cd slack_emoji_register
pip install -r equirements.txt
```

## Usage
```
python emoji_register.py "/path/to/imagefile" 
```

## OPTION
```
--name -n "emoji name"
--channel -ch "notification channel"
--config -c "config yaml file"
```

### config sample

* config.yaml
```yaml
teamname:
    YOUR TEAM NAME
email:
    YOUR E-MAIL ADDRESS
password:
    YOUR PASSWORD
channel:
    notification channel
```