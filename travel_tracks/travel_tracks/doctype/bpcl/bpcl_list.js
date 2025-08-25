console.log("BPCL listview js loaded!");

frappe.listview_settings['BPCL'] = {
    onload: function(listview) {
        console.log("Custom listview for BPCL loaded");  

        listview.page.add_inner_button(__('Register Company'), () => {
            console.log("Register Company button clicked");  

            let d = new frappe.ui.Dialog({
                title: 'Register Transport Company',
                fields: [
                    { label: 'company name', fieldname: 'company_name', fieldtype: 'Data', reqd: 1 },
                    { label: 'Email', fieldname: 'email', fieldtype: 'Data', reqd: 1 },
                    { label: 'Phone', fieldname: 'phone', fieldtype: 'Data', reqd: 1 },
                ],
                primary_action_label: 'Submit',
                primary_action(values) {
                    frappe.call({
                        method: 'travel_tracks.travel_tracks.doctype.bpcl.bpcl.registration',
                        args: values,
                        callback: function(r) {
                            if (!r.exc) {
                                frappe.msgprint(r.message.message);
                                d.hide();
                            }
                        }
                    });
                }
            });
            d.show();
        });
    }
};
