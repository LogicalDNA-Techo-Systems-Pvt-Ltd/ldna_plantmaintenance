 
(function() {
    function getRoleBreadcrumb() {
        const roleBreadcrumbs = {
            'Maintenance Manager': '/app/manager',
            'Maintenance User': '/app/maintenance-user',
            'System Manager': '/app/system-workspace',
            'Process Manager': '/app/manager'
        };

        const role = frappe.user_roles.find(r => roleBreadcrumbs[r]);
        return role ? `<a href="${roleBreadcrumbs[role]}">${role}</a>` : 
                       `<a href="/app/activity-group">Activity Group</a>`;
    }

    function updateBreadcrumbs(doctype, docname, isNew) {
        $(document).ready(function() {
            let breadcrumbs = $('#navbar-breadcrumbs').empty();

            let breadcrumbString = '';

            breadcrumbString += getRoleBreadcrumb();

            breadcrumbString += `  <a href="/app/${frappe.router.slug(doctype)}">${doctype}</a>`;

            if (isNew) {
                breadcrumbString += ` > New ${doctype}`;
            } else if (docname) {
                breadcrumbString += ` > ${__(docname)}`;
            }

            breadcrumbs.append(`<li class="breadcrumb-item">${breadcrumbString}</li>`);
        });
    }

    const doctypes = ['Equipment', 'Activity Group', 'Activity', 'Parameter','Task Detail'];

    doctypes.forEach(doctype => {
        frappe.ui.form.on(doctype, {
            refresh: function(frm) {
                const isNew = frm.is_new();
                updateBreadcrumbs(doctype, frm.doc.name, isNew);
            }
        });

        frappe.listview_settings[doctype] = {
            refresh: function(listview) {
                updateBreadcrumbs(doctype, null, false);   
            }
        };
    });
})();




