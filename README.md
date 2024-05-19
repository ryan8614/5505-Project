# Project name
NFT Marketplace
## Application introduction

Our NFT Marketplace aims to provide a trading platform for all users, where users are allowed to create their respective accounts to trade NFT fragments and collect NFT.

 When each user is first created and logged in, each user account will be set to have the same value. There are two ways for users to obtain NFT fragments. 

- The first way is to go to the lottery interface of the dashboard page to draw NFT fragments and obtain NFT fragments; 

- The second way is to go to the marketplace page to purchase the NFT fragments they need. After users extract NFT fragments, these fragments will appear in my fragment on the dashboard. In this container, users can freely adjust the transaction status and price of each of their own NFT fragments.

When the user needs an exact NFT fragment, he can go to the marketplace page and enter the desired NFT keyword into the search box. The platform will retrieve the content entered by the user and return results to the user to help the user purchase it. Wanted nft fragment.

How to increase your balance?

- Each user will receive 50 ETH as initial capital when they first register.
- Users can earn additional income by trading their own nft fragments.

- Finally, when the user collects a certain series of nft fragments, the user can go to the market place to redeem the prize and get the bonus.

## Team member

| UWA Student ID | Name | GitHub User Name |
|:------:|:----:|:--------------:|
| 24023844 | Shaohong Zheng | Shaohongzheng |
| 23691038 | Yike Chang | ryan8614 |
| 23941952 | Min Zhang | JasAAA |
| 23254894 | Yifei Tang | yifei-T |

## Instrctions to launch application

Python Version: 3.9

To launch this application, follow the steps below

1. Clone this repository to your local git directory：
    ```sh
    git clone https://github.com/ryan8614/5505-Project.git
    ```
2. Go to the git project directory：
    ```sh
    cd local-git-repo/5505-Project
    ```
3. Install required packages：
    ```sh
    pip install -r requirements.txt
    ```
4. Run server.py：
    ```sh
    python server.py
    ```

The application should run on `http://localhost:5001` 

## Instruction to run tests

To run your application's tests, follow these steps:

1. Make sure you are in the root directory of your project：
    ```sh
    cd your-repo-name
    ```

2. Run test command: 

    - Unit Tests

      ```
      python  -m unittest test/unit_test.py
      ```

    - Selenium Tests

      ```
      python server.py & python -m unittest test/selenium_test.py
      ```

       or you need to keep the server running first then excute:

      ```
      python -m unittest test/selenium_test.py
      ```

      

3. The test results will be displayed in the terminal window.

---

