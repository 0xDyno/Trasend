# 0.1.3. Trasend
What is it?
> That's about 1.5k+ lines of code that allow you to send TXs, native coin like ETH or smart contracts like ERC-20, depending on the network you connect to. In just three clicks, you can send hundreds of TXs from one wallet to many others. An ETH transaction typically takes 0.4 seconds, while an ERC-20 transaction takes 0.7 seconds. So you have to only set up the app, make 3 clicks and 1k transactions will be sent in 8-12 mins. It's free to test on Goerli Testnet.

User Settings (file user_settings.py):
> 1. RPC_Point - use default or your own 
> 2. max_connections - max requests to RPC at time, default 20 (you can try to use more with your private Node, services drop connection when there are more, than 30 connections pee moment).
> 3. update_gas - the app updates gas every N seconds.
> 4. multiply_gas / multiply_gas_price / and multiply_priority (1.1-2.3, etc.) - multiplies usual required gas amount (received live from blockchain). 
> 5. min_gas_price / min_priority (in gwei) - you can set up minimum gas price for TXs. Remember, you will not pay all gas_price you set, it will take only required. But all priority will go to the validators (miners).

Currently, the app supports next blockchains:</br >
**Mainnet**: Ethereum, BNB, Arbitrum, Matic, Avalanche, Fantom, Moonbeam</br >
**Testnet**: ETH-Goerli, BNB, Arbitrum_Goerli, Avalanche_Fuji, Fantom

So, the "interface" looks like this:
![Interface](/img/menu.png "Interface")

Now, you just need to click on the buttons and follow the instructions. You can:
- **Save / Load wallets** (you don't have to enter them every time), check Wallets + TXs, check all TXs and for 1 acc (only TXs that were made from with the app).
- **Add your wallet or Generant** as many, as you wish wallets (up to 1000 - that's solid recommendation).
- **Export wallets to file, import from file** (format "private_key address label", separated with spaces)
- **Deletes all TXs or Wallets**: (All / Last N / First N, some). To delete you can write in one line many numbers of labels or addresses, separated with spaces.
Example: 1 2 57 best_wallet 0xd9c2d319cd7e6177336b0a9c93c21cb48d84fb54, where 1, 2 & 57 - wallets numbers, best_wallet - label and last one - address
- **Sending transaction** (native coin ETH/BNB/MATIC or Smart-Contracts). Two ways to send - any wallet(s) in the app **or** to addresses from a file (1 per line). And ofc, it will count all fees before sending and ask for confirmation.

Keep your key file in private folder safe. All saved data is encrypted, without the key you won't be able to load it again.
If you need any additional functionality - DM me.

How difficult to install?

>Not too difficult, but still requires some time, hit me if you need help. Instruction:</br >
>1. You have to install Python v3.10</br >
>2. Clone this git (or download ZIP and unzip it)</br >
>3. Open terminal (command line), go to the folder and write: **pip install -r requirements.txt**</br >
>4. If it's okay - Congrats not you can start the app, If not - read the output and install additional tools it asks</br >

> To start the app write **python3 main.py**</br >
P.S.: if you have any Python IDE - it's better to set up venv separately
P.P.S.: if Python3 doesn't work - try Python, it words different depends on the system

## Attention
The code was tested for all Testnets, but only a little for Mainnets. Use with care.

I don't take responsibility for any potential losses.

Telegram: @i0xDyno