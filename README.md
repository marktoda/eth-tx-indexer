# Ethereum Transaction Indexer

Connects to an Ethereum full node and builds a database of the full transaction history of the blockchain.
This indexer takes special note of contract transactions, by keeping track of method IDs and deployed contracts.

## Requirements
`python -m pip install -r requirements.txt`

Also, a running instance of [MongoDb](https://www.mongodb.com/download-center)

## Configuration
#### Full Node
To work properly, the indexer needs to be pointed at a full node running the Ethereum RPC. 
Infura works great, just add the project id to `config.json:infura`
#### Mongo
Add Mongo host and port to `config.json:mongo`
#### Logging
The indexer logs to a file. Configure the file in `config.json:logging`
#### Performance
The indexer threads heavily when first synchronizing with the chain.
Customize the threading level in `config.json:indexer`
I suggest making this number as high as possible. My computer crashes anywhere above 20 unfortunately

## Start
`python indexer.py`