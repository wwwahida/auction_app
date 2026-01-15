# ECS639U Group Coursework — Swift Bid (Auction App)

Module leader: Paulo Oliva <p.oliva@qmul.ac.uk>

Swift Bid is a Django + Vue single-page auction application where users can sign up, post auction listings, bid on items, view bid history, ask questions on listings, and receive winner emails when auctions end.

---

## Group Members & Contributions

### Ahmed Khan (AhmedKhan7860 / ec23200)
- **Assigned:** Signup/registration flow, item detail page, search feature.
- **Actually did:** Implemented the search feature, and built the home page functionality for creating/posting auction items. Built and integrated the signup form with validation and created the item detail page (page for each listing).  

### Danyal Kasu (Dkasu / ec23224)
- **Assigned:** Authentication/profile-related features, frontend routing, Q&A forum.
- **Actually did:** Implemented Profile page + routing, profile editing functionality, logout feature, and improvements to authentication flow and templates/UI, implemented per-item Q&A forum

### Wahida Rahman (wwwahida / ec23372)
- **Assigned:** Core auction functionality (bidding, Q&A forum, auction-end email), App deployment
- **Actually did:** Improved the search feature and item detail page UI, implemented bidding end-to-end (backend validation + frontend BidModal + price updates), added bid history + seller username display, improvements to per-item Q&A forum, and created the auction closing command that emails winners. Deployed the application on OpenShift

---

## Deployed Application URL
- **URL:** group-26-web-apps-ec23372.apps.a.comp-teach.qmul.ac.uk

---

## Admin Account (Django Admin)
- **Admin URL:** `/admin/`
- **Username:** admin
- **Password:** admin123

---

## Test Users

1. **Username:** testuser1 
   **Password:** Password123!

2. **Username:** testuser2  
   **Password:** Password123!

3. **Username:** testuser3  
   **Password:** Password123!

4. **Username:** testuser4  
   **Password:** Password123!

5. **Username:** testuser5  
   **Password:** Password123!

---

## Key Features

### Auctions & Listings
- Browse active listings
- View listing details (with countdown)
- Seller username shown on item page

### Bidding
- Bid modal UI with dynamic “suggested minimum” placeholder
- Server-side validation:
  - Must be logged in
  - Cannot bid on your own listing
  - Must bid above current price
  - Cannot bid after auction end
- Bid history shown on item page (recent bids)

### Q&A Forum Per Listing
- Each listing has its own separate Q&A forum
- Users can post questions under a listing
- Replies are thread-based and displayed under each question
- Reply badges indicate:
  - **Lister/Owner**
  - **Asker**
- Reply permissions support back-and-forth between the listing owner and the question asker

### Auction End Email
- Management command closes auctions and emails winners:
  - `python manage.py close_auctions`
- Auctions are marked processed to prevent duplicate winner emails

---

## Local Development

To run this project on your development machine:

1. Create and activate a conda environment.

2. Download this repo and add the files to your own private repo.

3. Install Python dependencies (main folder):

    ```console
    $ pip install -r requirements.txt
    ```

4. Create a development database:

    ```console
    $ python manage.py migrate
    ```

5. Install JavaScript dependencies (from the `frontend` folder):

    ```console
    $ npm install
    ```

6. Start the Django development server (main folder):

    ```console
    $ python manage.py runserver
    ```

7. Start the Vue dev server (from the `frontend` folder):

    ```console
    $ npm run dev
    ```

8. Open your browser and go to:
   - http://localhost:5173

---

## OpenShift Deployment

Once your project is ready to be deployed you will need to build the Vue app and place it in Django’s static folder.

1. The build command in `package.json` and the `vite.config.ts` file have already been modified so that when running `npm run build` (on Mac/Linux) the generated JS/CSS will be placed in the Django static folder, and the `index.html` file will be placed in the templates folder:

    ```console
    $ npm run build
    ```

    If using Windows:

    ```console
    $ npm run build-windows
    ```

2. Follow the QM+ instructions on how to deploy your app on EECS OpenShift.

---

## License

This code is dedicated to the public domain to the maximum extent permitted by applicable law, pursuant to CC0:
http://creativecommons.org/publicdomain/zero/1.0/


