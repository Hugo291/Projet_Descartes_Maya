from app import application
from app.routes.scan import threadScan
from app.models.DataBase import PDF_ERROR, PDF_SUCCESS, PDF_IN_PROGRESS, PDF_WAIT


@application.template_filter('value_state_file')
def value_status_file(state_number):
    return {
        PDF_WAIT: '<span class="text-warning font-weight-bold">Waiting</span>',
        PDF_IN_PROGRESS: '<span class="text-info font-weight-bold">In progress ( ' + str(
            threadScan.get_percent()) + ' % )</span>',
        PDF_SUCCESS: '<span class="text-success font-weight-bold">Finished</span>',
        PDF_ERROR: '<span class="text-danger font-weight-bold">Failure</span>'
    }[state_number]
