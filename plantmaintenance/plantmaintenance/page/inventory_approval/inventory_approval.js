frappe.pages['inventory-approval'].on_page_load = function(wrapper) {
    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Inventory Approval',
        single_column: true 
    });

    let $task_container = $('<div>').appendTo(page.body);

    let $table = $('<table class="table table-bordered">').appendTo($task_container);
    $table.append(`
        <thead>
            <tr>
                <th><input type="checkbox" id="select-all"></th> <!-- Master checkbox -->
                <th>No</th> 
                <th>Task Name</th>
                <th>Material Code</th>
                <th>Material Name</th>
                <th>Available Quantity</th>
                <th>Required Quantity</th>
                <th>Shortage</th>
                <th>Status</th>
                <th>Approval Date</th>
                <th>Issued Date</th>
            </tr>
        </thead>
        <tbody></tbody>
    `);

    let $tbody = $table.find('tbody');
    let index = 1; 

    frappe.call({
        method: 'plantmaintenance.plantmaintenance.page.inventory_approval.inventory_approval.get_task_details',
        callback: function(response) {
            if (response.message) {
                response.message.forEach(function(task_detail) {
                    if (task_detail.materials.length > 0) {
                        task_detail.materials.forEach(function(material) {
                            $tbody.append(`
                                <tr>
                                    <td><input type="checkbox" class="material-checkbox" data-task="${task_detail.task_name}" data-material="${material.material_code}"></td>
                                    <td>${index++}</td>
                                    <td>${task_detail.task_name}</td>
                                    <td>${material.material_code}</td>
                                    <td>${material.material_name}</td>
                                    <td>${material.available_quantity}</td>
                                    <td>${material.required_quantity}</td>
                                    <td>${material.shortage}</td>
                                    <td>${material.status}</td>
                                    <td>${frappe.datetime.str_to_user(material.approval_date)}</td>
                                    <td>${frappe.datetime.str_to_user(material.issued_date)}</td>
                                </tr>
                            `);
                        });
                    }
                });
            }
        }
    });

    let $approve_button = $('<button class="btn btn-primary">Approve</button>').appendTo($task_container);

    $approve_button.on('click', function() {
        let selectedMaterials = [];
        $task_container.find('.material-checkbox:checked').each(function() {
            let row = $(this).closest('tr');
            selectedMaterials.push({
                task_name: row.find('td:eq(2)').text(),
                material_code: row.find('td:eq(3)').text(),
                available_quantity: row.find('td:eq(5)').text(),
                required_quantity: row.find('td:eq(6)').text()
            });
        });

        if (selectedMaterials.length > 0) {
            frappe.call({
                method: 'plantmaintenance.plantmaintenance.page.inventory_approval.inventory_approval.approve_materials',
                args: {
                    materials: selectedMaterials
                },
                callback: function(response) {
                    if (response.message) {
                        frappe.msgprint(response.message);
                    }
                }
            });
        } else {
            frappe.msgprint('No materials selected.');
        }
    });

    $task_container.on('change', '#select-all', function() {
        let isChecked = $(this).prop('checked');
        $task_container.find('.material-checkbox').prop('checked', isChecked);
    });
};

