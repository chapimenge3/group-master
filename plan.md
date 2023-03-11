# Plan for Group Master Telegram Bot

## Models

### User

- id: int[primary key]
- first_name: string
- last_name: string
- username: string
- email: string[Null]

### Groups

- id: int[primary key]
- name: string
- price: int
- duration: int

### Memberships

- id: int[primary key]
- user_id: int[foreign key]
- group_id: int[foreign key]
- start_date: date
- end_date: date
- status: string
- transaction_id: string
- created_at: datetime
- updated_at: datetime

### Transactions

- id: int[primary key]
- user_id: int[foreign key]
- group_id: int[foreign key]
- amount: int
- status: string
- payment_method: string
- created_at: datetime
- updated_at: datetime

## Flow

- User /start
- show groups list
- select group
- check if the user is a member of the group
  - then show the remaining days until the end of the membership
  - else show the price and duration of the group

- up on selection show payment methods
- select payment method
- Send payment link to the user

User pays

- return to the bot
- verify payment
  - if payment is successful
        - create membership
        - update transaction
        - show success message
        - send invitation to the group
  - else
        - show error message

USER Request JOIN GROUP

- check if the user membership is valid
  - if valid
            - accept the request
  - else
            - reject the request
