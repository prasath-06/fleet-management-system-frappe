frappe.ui.form.on("BPCL", {
    refresh(frm) {

        // Add Vehicles button
        frm.add_custom_button('Add vehicles', () => {
            let dialog = new frappe.ui.Dialog({
                title: 'Registration',
                fields: [
                    {
                        label: 'Vehicle',
                        fieldname: 'vehicle',
                        fieldtype: 'Table',
                        fields: [
                            {
                                label: 'Vehicle Details',
                                fieldname: 'vehicle_details',
                                fieldtype: 'Link',
                                options: 'Vehicle',
                                in_list_view: 1
                            },
                        ]
                    }
                ],
                primary_action_label: 'Create Card',
                primary_action(values) {
                    frappe.call({
                        method: 'travel_tracks.travel_tracks.doctype.bpcl.bpcl.add_vehicles',
                        args: {
                            vehicles: values.vehicle,
                            bpcl_docname: frm.doc.name 
                        },
                        callback: function (r) {
                            if (!r.exc) {
                                frappe.msgprint(r.message.message);
                                dialog.hide();
                            }
                        }
                    });
                }
            });

            dialog.show();
        });

        frm.add_custom_button('Edit PIN', () => {
            let table_data = (frm.doc.bpcl || []).map(row => ({
                vehicles: row.vehicles,
                card: row.card,
                pin: row.pin,
            }));

           

            let dialog = new frappe.ui.Dialog({
                title: 'Edit PIN',
                size: 'large',
                fields: [
                    {
                        label: 'Vehicles',
                        fieldname: 'vehicle',
                        fieldtype: 'Table',
                        in_place_edit: true,
                        fields: [
                            {
                                label: 'Card',
                                fieldname: 'card',
                                fieldtype: 'Data',
                                in_list_view: true
                            },
                            {
                                label: 'PIN',
                                fieldname: 'pin',
                                fieldtype: 'Int',
                                in_list_view: true
                            },
                        ]
                    }
                ],
                primary_action_label: 'Update PINs',
                primary_action(values) {
                    frappe.call({
                        method: 'travel_tracks.travel_tracks.doctype.bpcl.bpcl.update_vehicle_pins',
                        args: {
                            vehicle: values.vehicle,
                            bpcl_docname: frm.doc.name 
                        },
                        callback: function (r) {
                            if (!r.exc) {
                                frappe.msgprint("PINs updated successfully");
                                dialog.hide();
                            } else {
                                frappe.msgprint("Error updating PINs: " + r.message);
                            }
                        }
                    });
                }
            });

            dialog.set_value('vehicle', table_data);

            dialog.show();
        });

    }
});
