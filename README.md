Wallet application

How to run application? See it below.

1. Create directory for project - mkdir test_project
2. Go to test_project directory - cd test_project
3. Create repository - run command git init with Git Bush
4. Clone remote repository - run command git clone https://github.com/alexugalek/wallet.git
5. Open test_project in Pycharm
6. Set virtual environment - File/Settings/Project:wallet/Project Interpreter (click on wheel in high right corner)
7. Open first Terminal window
8. Go to wallet directory - cd wallet
9. Install all requirements - pip install -r requirements.txt
10. Make migrations - python manage.py makemigrations
11. Migrate - python manage.py migrate
12. Set telegram bot token in settings.py - TOKEN = '946100261:AAGEoXG4xienoDYUbupjvWgJ_gh0x1mw7pI'
13. Run server - python manage.py runserver
14. You can register as new user or use admin credentials:
    username: admin
    password: root_root
15. Open second Terminal window
16. Go to wallet directory - cd wallet
17. Run telegram bot - python manage.py bot
18. Open http://127.0.0.1:8000/ in your browser

Well done!

Now application ready to use

How it works?

This simple application will create statistic of all expenses you will send
1. "Home" link in navigation bar - just simple information about functionality of application
2. "Registration" link in navigation bar - link for registration(after success registration will be auto login)
3. "Login" link in navigation bar - link for login
4. When user is authenticated few new links will appear in navigation bar .
5. "Logout" link - link to logout
5. "Edit personal info" link - there you can change your username and email
6. "Report settings" link - settings to control expenses limits:
                            - in each category, if report is in active status,
                            the amount of money that user can spend today to reach the limit will be shown
                            on "Info" link 
7. "Info" link in navigation bar - There is statistic of current month expenses:
   - first row of statistic: - show total balance user can spend today as difference between total daily expenses 
                             and total limit values where report is in active status
                             - show balance in each category where report is in active status user can spend today 
                             as difference between daily expenses and limit value
   - rest rows of statistic: - show link to get detail view of daily expenses
                             - show number of bills
                             - show expenses value in each category
8. "Info" link in navigation bar - There is toolbar with date filter to get statistic from previous months
9. "Info" link in navigation bar - There is button to send statistic to email(e-mail with attachment file)
10. "Month day, year" links - There is detail statistic for selected day with bill photos and 
                             "View/Edit" and "Delete" links for each record
11. "Add Expenses" link - Modal form to add expenses(USD currency only available)
12. "Add Bill" link - Modal form to add bills photos(maximum size 10Mb) with resizing when save to storage
13. Find "@Wallet_economy_bot" account in telegram and start with any message. 
    All instructions will be in replies.
    With telegram bot user can easily add expenses ("category_name value" message)
    and get know information ("balance" message) about:
    - How much money was spent today 
    - How much money user can spent today to reach total limit value(forms as for "Info" link: see 7 point)
                       
     
                                    
    
