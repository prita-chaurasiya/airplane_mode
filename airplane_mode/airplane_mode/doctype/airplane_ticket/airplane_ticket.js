frappe.ui.form.on("Airplane Ticket", {
    ticket_price: function(frm) {
        calculate(frm);
    },
    tax_rate: function(frm) {
        calculate(frm);
    }
});

function calculate(frm) {

    let price = frm.doc.ticket_price || 0;

    let tax_map = {
        "0%": 0,
        "5%": 5,
        "12%": 12,
        "18%": 18,
        "28%": 28
    };

    let tax = tax_map[frm.doc.tax_rate] || 0;

    let tax_amount = (price * tax) / 100;
    let total = price + tax_amount;

    frm.set_value("tax_amount", tax_amount);
    frm.set_value("total_amount", total);
}