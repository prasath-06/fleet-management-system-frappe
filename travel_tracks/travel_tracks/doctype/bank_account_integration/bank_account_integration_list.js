console.log("BPCL listview js loaded!");

frappe.listview_settings['Bank Account Integration'] = {
    onload: function(listview) {
        console.log("Custom listview for BPCL loaded");  

        listview.page.add_inner_button(__('Register Account'), () => {
            console.log("Register Company button clicked");  

            let d = new frappe.ui.Dialog({
                title: 'Account Registration',
                fields: [
                    { label: 'Account Name', fieldname: 'account_name', fieldtype: 'Data', reqd: 1 },
                    { label: 'Phone', fieldname: 'phone', fieldtype: 'Data', reqd: 1 },
                    { label: 'Email', fieldname: 'email', fieldtype: 'Data', reqd: 1 },
                    { label: 'Address', fieldname: 'address', fieldtype: 'Data', reqd: 1 },
                    { label: 'Account Type', fieldname: 'account_type', fieldtype: 'Select',options:['Savings','Current'], reqd: 1 },
                   
                ],
                primary_action_label: 'Submit',
                primary_action(values) {
                    frappe.call({
                        method: 'travel_tracks.travel_tracks.doctype.bank_account_integration.bank_account_integration.account_integration',
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
