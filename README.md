# Chairing App

## 📚 Welcome, Study Enthusiast! 🚀

**Do you love studying?** Or maybe you'd like to help others who are looking for the perfect place to get some work done? 💡 **Well, you're in the right place!** Chairing is here to bring students together with the best study spots around. 

## 📖 Here You Can Read the Instructions!

To get started, **follow these simple steps** and make the most out of the Chairing app:

### 1. **Sign Up or Log In**

First things first, create your account. 🎉 Just click on **"Sign Up"** on the home page and fill out your details. If you already have an account, **just log in** and you're good to go!

### 2. **Choose Your Role** – Help others or Reserve Your Spot!

After logging in, **choose what you want to do**:

- **Upload Your Location**: Do you have a **study-friendly place** (like a cozy living room or a study lounge) where others can come study? You can **upload your location** so other students can find a great place to study! Simply go to the **"Upload Location"** page and add your place with all the necessary details.

- **Make a Reservation**: Or perhaps you want to find a place to study? Choose a location from the available options and **reserve a time slot** that suits you! You can do this easily by visiting the **"Reservations"** page.

### 3. **Make a Reservation**

Once you’ve chosen a location, **select the available time slot** for your study session. 📅 It's easy to book a time that works best for you!

### 4. **Done! Study, Collaborate, and Enjoy!**

You’re all set to enjoy your study session! Whether you're helping others or reserving a spot for yourself, **Chairing is your go-to place for productive study sessions**. 🎓💪

## Features:

- **User Accounts**: Sign up, log in, and manage your account.
- **Upload Location**: Share your own study-friendly locations with others.
- **Reservation System**: Reserve time slots for available locations.
- **Location Search**: Find the best study spots based on your needs.

## 🎯 Try it Now!

Start using **Chairing** today to find your favorite study spot, help others, and stay productive! Happy studying! 💼🎉

---
---

## How Our Code Works
In our demo video, we explain the basic functionalities of our site.

### Layout  
We began by designing a template in Figma, which served as a working document throughout development. As our website evolved, we continuously updated the Figma file to reflect the changes. The final Figma version includes the structure for most of our website's pages.  

For the homepage, main page, login, and signup pages, we drew inspiration from an online template. This approach gave our website a more polished and professional appearance.  

- **Demo Video**: [Basic Functionalities Chairing](https://vicvereecke2.wistia.com/medias/omxv00fxo0)  
- **Figma File**: [Chairing Design](https://www.figma.com/design/lpcroGTkpFvW8u9mU9Tbih/Chairing?node-id=0-1&t=jZgN5xBRTQklAzLF-1)  
- **Template Reference**: [React Markit Template](https://react-markit.vercel.app/home)  

### File-Specific Details  
Below, you can find explanations about various parts of our code, along with the functions we used. These functions are located in the `routes.py` file.  

---

#### `home.html`  
The reviews displayed on this page are for layout purposes only and are not part of the actual review system.  

**Function used**: `home()`  

---

#### `login.html` & `signup.html`  
- **Signup Process**:  
  - Users must provide a username and phone number (both mandatory).  
  - If required fields are left blank, an error message is displayed.  
  - Passwords are required alongside a confirmation password to ensure accuracy. If the two passwords do not match, an error message is shown.  

- **Login Process**:  
  - The username and password must match an existing record in our database. If either is incorrect, an error is displayed.  

- **Password Security**:  
  For privacy, we store only hashed versions of passwords in our database. This ensures that no one can view or retrieve the original passwords.  

- **Logout Option**:  
  After logging in, you can log out from any page by clicking the **Logout** button in the upper right corner.

**Functions used**: `login()`, `signup()` & `logout()`

---

### `main-page.html`  
**This Week's Highlighted Locations**:  
The highlighted locations are selected based on the highest ratings received during the previous week. This list updates every Monday at 00:00. The stars displayed in the containers represent the all-time average rating of each location (not just for the previous week).  

**Functions used**: `main_page()` & `get_highlighted_locations()`

---

### `account.html`  
#### **Personal Information**  
Here, you can update your username or phone number. When you make changes, the previous values are deleted from our database and replaced with the new ones.  

#### **Your Study Targets**  
- You can set two types of weekly targets:  
  1. **Study Time Target**: Tracks the total study time for this week.  
  2. **Study Sessions Target**: Counts the number of study sessions completed this week.  

- Targets are stored in the user table of the database and can be updated anytime.  

- Example:  
  - Today is Wednesday. On Monday, you had a reservation for 120 minutes, and on Thursday, you have a reservation planned for 90 minutes.  
  - You set your weekly targets to **3 hours of study time** and **2 sessions**.  
  - Before Thursday's reservation:  
    - Study progress: **2h00 of 3h00 done**  
    - Session progress: **1 of 2 sessions done**  
  - After Thursday's reservation:  
    - Study progress: **3h30 of 3h00 done** (goal achieved)  
    - Session progress: **2 of 2 sessions done** (goal achieved)  

- A congratulatory message will display when you achieve your weekly goals.  

#### **Student**  
- Displays your **average rating as a student**, rounded to the nearest integer. This rating is calculated from feedback received from the hosts of locations where you made reservations.  
- Below the rating, you can view your previous reservations, including any messages from the host.  
- If you haven’t made any reservations yet, this section will remain empty.  

#### **Location Owner**  
- Displays the **average rating of your location**, rounded to the nearest integer. This is based on all ratings received for your location.  
- You can also delete your location from this page. This action:  
  - Changes the location's status in the database from **active** to **deleted**.  
  - Updates the status of all future reservations for this location from **active** to **loc_del**, marking them as canceled.  
  - Notifies students of the cancellation.  

- Below this, you can see a list of users who have previously booked your location, along with any messages they may have left.  
- If you don’t have a location registered, this section will remain empty.  

**Functions used**: `account()`, `update_user_info()`, `delete_target(user, target_type)` & `delete_location()`

---

### `all-locations.html`  
This page displays all locations along with the following details:  
- Average rating  
- Type of location  
- Address  
- Number of available chairs  
- Opening hours  

**Important**:  
Reservations cannot be made directly from this page. It is intended for students to browse and decide where they might want to study.  

**Sorting and Filtering**:  
- **Sorting**:  
  - Locations can be sorted by **rating** or by **available chairs** to adjust the display order.  
- **Filtering**:  
  - Filters include **opening day**, **location (city and country)**, and **type of location**.  
  - Multiple filters can be applied simultaneously to help students find their ideal location.  

**Function used**: `all_locations()`

---

### `make-reservation.html` & `select-location.html`  
#### `make-reservation.html`  
Students can make a reservation by specifying:  
1. **Date and time** they want to study.  
2. **Duration** of the study session.  
3. **Number of people** attending.  

**Note**: All fields are mandatory.  

#### `select-location.html`  
This page displays a list of locations that meet the selected criteria, including feasible opening hours and available seats. Students can easily choose their desired study location from the list.  

**Functions used**: `make_reservation()`, `select_location()`, `confirm_reservation()` & `filter_available_locations(reservation_datetime, study_time, number_of_guests)`

---

### `your-reservations.html`  
#### **Current Reservations**  
- Displays all reservations that are still planned for the future.  
- Includes the **username** and **phone number** of the host for easy contact.  
- Reservations can be canceled directly from this page.  
  - Cancellation updates the reservation status in the database from **active** to **canceled**.  
  - **Note**: Cancellations cannot be undone.  

#### **Past Reservations**  
- Reservations that have already occurred are moved to the **Past Reservations** section.  
- Students can:  
  - **Give a star rating** to the location.  
  - **Add a personal message** for the host (optional).  
  - Edit these ratings or messages at any time afterward.  

**Functions used**: `your_reservations()`, `cancel_reservation()` `update_location_rating(location_id)` & `expire_old_reservations(reservation_datetime, study_time, number_of_guests)`

---

### `upload-location.html`  
If you do not currently have a location with a status of **active**, you can upload your location here by providing the following details:  
- **Location Name**  
- **Type of Location**  
- **Number of Available Seats**  
- **Address**  

**Opening Hours**:  
- Select the opening hours for each day.  
- For days when the location is closed, simply choose the "Closed" option.  

**Location Image**:  
- Choose one of six predefined pictures that best represents your location.  

If you already have a location with a status of **active**, a message will display stating that you cannot upload another location.  

**Functions used**: `upload_location()` & `format_time(hour, minute)`

---

### `your-bookings.html`  
#### **Current Bookings**  
- Displays reservations with a status of **active**, including:  
  - **Username**  
  - **Phone Number**  
  - **Student Rating**  
  - Reservation details  

#### **Past Bookings**  
- Reservations that have occurred are moved to the **Past Bookings** section with a status of **expired**.  
- For each past booking, you can:  
  - Provide a **star rating** for the student.  
  - Add a **personal message** to the student (optional).  
- These reviews can be updated at any time.  

**Functions used**: `your_bookings()` & `update_user_rating(user_id)`

---

### `about.html` & `about-us.html`
These pages provide information about the platform and include two counters:
1. The total number of reservations with an **expired** status.
2. The total number of locations in the database.

The difference between `about.html` and `about-us.html` is in the available navigation options:
- `about-us.html` restricts users to only the **Home**, **Login**, and **Sign Up** pages, ensuring that non-logged-in users cannot access certain areas.
- `about.html` allows navigation to all other pages

**Functions used**: `about()` & `about_us()`
