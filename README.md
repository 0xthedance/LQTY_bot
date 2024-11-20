# Liquidation bot for Liquity protocol

A liquidation bot for Liquity Protocol created using APE Framework and Silverback library.

## Requirements
Install requirements and Ape plugins:

```sh
pip install -r requirements.txt
ape plugins install .

```

## Configuration


The  Constants.py file contains the bot configuration. But at the very least, the following environmental variables should be set:

```sh
#Provider token.It is neccessary a provider that supports websockets to run the bot. If you want to use Alchemy to run this example, you will need a Alchemy API key for Ethereum mainnet.Go to Alchemy, create an account, then create an application in their dashboard, and copy the API Key.
export WEB3_ALCHEMY_PROJECT_ID=<value-of-secret-key>

# APE account configuration (https://docs.apeworx.io/ape/stable/userguides/accounts.html#importing-existing-accounts)
export APE_ACCOUNTS_$ALIAS_PASSPHRASE=<ape-account-password>
export ACCOUNT_ALIAS=<ape-account-alias>

#logging configuration
export LOG_EMAIL
export EMAIL_PASSWORD
```


## Usage

```sh
silverback run "main:bot" --network:mainnet:alchemy
```

## Run it in Sepolia

```sh
silverback run "main:bot" --network:sepolia:alchemy
```
