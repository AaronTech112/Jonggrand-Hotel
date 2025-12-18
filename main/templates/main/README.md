# Jonggrand Hotel Frontend

This is the frontend project for Jonggrand Hotel, a luxury hotel website. It is built with HTML5, CSS3, JavaScript, and Bootstrap 5.

## Features
- **Responsive Design**: Mobile-first approach ensuring great experience on all devices.
- **Booking System**: Multi-step booking modal with guest info, room selection, extras, and payment summary.
- **Payment Integration**: Placeholder for Flutterwave payment gateway.
- **Gallery**: Photo and video gallery with lightbox.
- **Event Booking**: Inquiry form for events and conferences.
- **Accessibility**: Basic ARIA labels and keyboard navigation support.

## Project Structure
```
/
├── assets/
│   ├── images/       # Hotel images and videos
│   └── logo.png      # Logo
├── css/
│   └── styles.css    # Custom styles and variables
├── js/
│   └── main.js       # Interactive logic (booking, modal, validation)
├── index.html        # Home page
├── rooms.html        # Rooms listing
├── room-detail.html  # Single room detail
├── events.html       # Events & Conference hall
├── gallery.html      # Multimedia gallery
├── about.html        # About Us, Vision, Mission
├── contact.html      # Contact form and map
├── 404.html          # Custom 404 page
└── README.md         # Documentation
```

## Setup & Usage
1.  **Open the Project**: Simply open `index.html` in any modern web browser. No server is strictly required for the frontend to look correct, but for better performance (especially with ES modules if used later) or testing APIs, use a local server (e.g., Live Server in VS Code).
2.  **Development**:
    -   Edit `css/styles.css` to change the color palette or fonts. CSS variables are defined at the top of the file.
    -   Edit `js/main.js` to modify the booking logic or validation.

## Backend Integration

### 1. Booking Availability
In `rooms.html` and `room-detail.html`, the availability is currently static.
*   **To Implement**: Connect the "Check Availability" form to your backend API.
*   **Location**: Look for the `<form>` elements in the booking bar and `js/main.js`.

### 2. Payment (Flutterwave)
The payment process is simulated in `js/main.js`.
*   **To Implement**:
    1.  Get your Public Key from the Flutterwave Dashboard.
    2.  Uncomment the `FlutterwaveCheckout` code block in `js/main.js`.
    3.  Replace `FLWPUBK_TEST-SANDBOX-DEMO-KEY-X` with your actual key.
    4.  Ensure your backend verifies the transaction using the `transaction_id` returned in the `callback` function.

### 3. Contact & Event Forms
The forms currently alert a success message.
*   **To Implement**: Update the `submit` event listeners in `js/main.js` (or inline scripts in `events.html`) to send a POST request to your backend endpoint (e.g., `/api/contact` or `/api/inquiry`).

## Customization
*   **Colors**: You can switch palettes in `css/styles.css` by commenting/uncommenting the variables in the `:root` selector.
*   **Images**: Replace images in `assets/images/` and update the `src` attributes in the HTML files.

## Credits
-   Bootstrap 5
-   FontAwesome
-   Google Fonts (Lato, Playfair Display)
