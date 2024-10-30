# Twitter->Slack Bot

The Twitter->Slack Bot is a tool designed to monitor specified Twitter accounts and send updates to a Slack channel. This bot helps teams stay informed about important tweets without having to constantly check Twitter.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

What things you need to install the software and how to install them

- Kubernetes

or

- Python12.7

### Installing(Python)

If you want to run dev, you should do it.

1. Clone this repo
2. Install pip package with requirements.txt
3. Set environment secrets

```sh
DB_PASSWORD=DB_PASSWORD
SLACK_APP_TOKEN=TOKEN
SLACK_BOT_TOKEN=TOKEN
TWITTER_AUTH_INFO_1=TWITTER_EMAIL
TWITTER_AUTH_INFO_2=TWITTER_USERNAME
TWITTER_PASSWORD=TWITTER_PASSWORD
```

4. Run `python main.py`

## Deployment

Fork this repo and deploy with ArgoCD.

## Built With

* [twikit](https://github.com/d60/twikit) - The twitter API wrappar
* ArgoCD - Dependency Management
- [SQLAlchemy](https://www.sqlalchemy.org/) - DB ORM

## Contributing

Please read [CONTRIBUTING.md](./CONTRIBUTING.md) for details on our code of conduct, and the process for submitting pull requests to us.

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/your/project/tags).

## Authors

* **YuitoAkatsuki** - [yuito-it](https://github.com/yuito-it)

See also the list of [contributors](https://github.com/yuito-it/TwitterSlackBot/contributors) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* Hat tip to anyone whose code was used
* Inspiration
* etc
