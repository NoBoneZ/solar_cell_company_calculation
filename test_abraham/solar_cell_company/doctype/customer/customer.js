// Copyright (c) 2025, NoBoneZ and contributors
// For license information, please see license.txt

// Frappe trigger events for the "Customer" Doctype
frappe.ui.form.on("Customer", {
    
    // Event triggered when the form is refreshed
    refresh(frm) {
        // Currently empty but can be used for UI updates or actions
    },

    // Event triggered before form validation
    validate(frm) {
        validate_user(frm); // Ensure user has the correct role before saving
    },

    // Event triggered before saving the form
    before_save(frm) {
        // Set the full name dynamically by concatenating first and last name
        frm.set_value("full_name", frm.doc.first_name + (frm.doc.last_name ? " " + frm.doc.last_name : ""));
    },

    // Event triggered when the email field is updated
    email(frm) { 
        validate_user(frm); // Revalidate the user when email is changed
    },
    setup: function(frm) {
        frm.set_query("user", function() {
            return {
                query: "test_abraham.solar_cell_company.doctype.customer.customer.get_customer_users"
            };
        });
    }
});

/**
 * Function to validate if the user has the "Customer" role
 * 
 * @param {Object} frm - The current form instance
 */
const validate_user = (frm) => {
    if (frm.doc.email) {
        frappe.call({
            method: "test_abraham.solar_cell_company.doctype.customer.customer.check_user_role",
            args: { email: frm.doc.email },

            // Callback function to handle the response
            callback: function (response) {
                if (!response.message.exists) {
                    frappe.throw("Only Users with Customer roles can be associated with the Customer document");
                }
            },

            // Error handling if the request fails
            error: function (err) {
                frappe.msgprint({
                    title: __("Permission Denied"),
                    message: err.message,
                    indicator: "red"
                });
            }
        });
    }
};

