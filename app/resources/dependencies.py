from .helpers import *


def get_project_role(user_id, project_code):
    project = get_dataset_node(project_code)
    if not project:
        error_msg = customized_error_template(ECustomizedError.PROJECT_NOT_FOUND)
        code = EAPIResponseCode.not_found
        return error_msg, code
    project_id = project.get("id")
    role_check_result = get_user_role(user_id, project_id)
    if role_check_result:
        role = role_check_result.get("r").get('type')
        code = EAPIResponseCode.success
        return role, code
    else:
        error_msg = customized_error_template(ECustomizedError.USER_NOT_IN_PROJECT)
        code = EAPIResponseCode.not_found
        return error_msg, code
