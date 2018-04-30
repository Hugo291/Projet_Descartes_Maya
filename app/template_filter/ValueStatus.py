from app import application
from app.routes.scan import threadScan


@application.template_filter('value_state_file')
def value_status_file(status_number):
    return {
        0: '<span class="text-warning font-weight-bold">Waiting</span>',
        1: '<span class="text-info font-weight-bold">In progress ( ' + str(threadScan.get_percent()) + ' % )</span>',
        2: '<span class="text-success font-weight-bold">Finished</span>',
        -1: '<span class="text-danger font-weight-bold">Failure</span>'
    }[status_number]
