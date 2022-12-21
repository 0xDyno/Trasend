# 0.1.2. Trasend
What is it?
> That's about 1.5k+ lines of code that allow you to send TXs, native coin like ETH or smart contracts like ERC-20, depending on the network you connect to. In just three clicks, you can send hundreds of TXs from one wallet to many others. An ETH transaction typically takes 0.4 seconds, while an ERC-20 transaction takes 0.7 seconds. So you have to only set up the app, make 3 clicks and 1k transactions will be sent in 8-12 mins. It's free to test on Goerli Testnet.

How difficult to install?

> You have to install python3 and clone this git. Not too difficult, hit me if you need help.

So, let's talk about settings. Open config.settings.py to make changes. I don't suggest changing all the settings, there could be errors then. You may be interested in:
1. RPC_Point - use Infura or Alchemist (can be changed in the app).
2. update_gas_every - the app updates gas every N seconds.
3. max_threads_per_time - default 20, you can try to use more with your private Node, but if there are more, than 30 connections per second -> Alchemist blocks connection.
4. multiply_gas / multiply_gas_price / and multiply_priority (1.1-2.3, etc.) - you know what it does, it multiplies the usual required gas amount. Then it determines whether the amount is greater or less than the minimum. Set the minimum if it is less.
5. min_gas_price / min_priority (in gwei) - you can set up minimum gas price for TXs. Remeber, you will not pay all gas_price you set, it will take only required. But all priority will go to the validators (miners).

Currently, the app supports only ETH & BNB mainnet, Goerli testnet. To open access to more chains - contact me.

So, the "interface" looks like this:
![Interface](/img/menu.png "Interface")

Now, you just need to click on the buttons and follow the instructions. You can:
- Save / Load wallets (you don't have to enter them every time), check Wallets + TXs, check all TXs and for 1 acc (only TXs that were made from with the app).
- Add your wallet or Generant as many, as you wish wallets (up to 1000 - that's solid recommendation).
- Import wallets to the file, export from the file (format "private_key address label", separated with spaces)
- Deletes all TXs & Wallets / / All / Last N / First N, some. To delete you can write in one line many numbers of labels or addresses, separated with spaces.
Example: 1 2 57 best_wallet 0xd9c2d319cd7e6177336b0a9c93c21cb48d84fb54, where 1, 2 & 57 - wallets numbers, best_wallet - label and last one - address
- Finally - Sending transaction. There are 2 variants to whom you can send. First - any wallet(s) in the app. Second - upload a file with receivers (just addresses, 1 per line). And ofc, it will count all fees before sending and ask for confirmation.

Keep your key file in private folder safe. All saved data is encrypted, without the key you won't load it again.
If you need any additional functionality - DM me.

## Attention
The code wasn't tested on ETH mainnet, so be careful.
I don't take responsibility for any potential losses