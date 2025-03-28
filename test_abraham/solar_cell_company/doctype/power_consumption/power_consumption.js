// Copyright (c) 2025, NoBoneZ and contributors
// For license information, please see license.txt

frappe.ui.form.on("Power Consumption", {
	refresh(frm) {

	},
    validate(frm){
        validate_future_dates(frm)
        
    }
});


const validate_future_dates = (frm) => {
    if (frm.doc.date && frm.doc.date > frappe.datetime.now_datetime()){
        frappe.throw("Power consumption can not be recorded for future dates")
    }


}