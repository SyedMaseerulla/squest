from squest_survey.models import Response, Question


def get_survey_var_list(job_template_survey):
    survey_variable_list = []
    if "spec" in job_template_survey:
        for survey_filed in job_template_survey["spec"]:
            survey_variable_list.append(survey_filed["variable"])
    return survey_variable_list


#TO-DO: fix pep8 @Nataraj
def check_extra_vars(request, response, questions, instance_squest):
        survey_variable_list = []
        survey_spec_var_list = []
        survey_spec_var_list = get_survey_var_list(response.template.operation.job_template.survey)
        print(f'{survey_spec_var_list = }')
        error = None
        # for question in questions:
        #     survey_variable_list.append(question.awx_variable_name)
        # print("survey_variable_list",survey_variable_list)
        # for var1 in survey_spec_var_list:
        #     if var1 not in survey_variable_list and response.type == Response.SURVEY:
        #         survey_vars_present = False
        #         error = f'All the variables defined in survey are not available in form'
        #         break
        #     elif var1 not in survey_variable_list and var1 not in instance_squest.spec.keys() and response.type == Response.NEW_OPERATION:
        #         print("var1", var1, response.type)
        #         error = f'All the variables defined in survey are not available in form or spec'
        for field_name in questions:
            if field_name.startswith('question_'):
                q_id = int(field_name.split('_')[1])
                question = Question.objects.get(pk=q_id)
                if question.type == Question.INFOMATION_TEXT:
                    continue
                if question.awx_variable_name:
                    survey_variable_list.append(question.awx_variable_name)
            if field_name.startswith("cascade_question_"):
                q_id = int(field_name.split("_")[2])
                question = Question.objects.get(pk=q_id)
                if question.awx_variable_name:
                    survey_variable_list.append(question.awx_variable_name)
        print(f'{survey_variable_list = }')
        for var in survey_spec_var_list:
            if var not in survey_variable_list and response.type == Response.SURVEY:
                print("var missing", var)
                error = f'All the variables defined in survey are not passed'
                break
            elif var not in survey_variable_list and var not in instance_squest.spec.keys() and response.type == Response.NEW_OPERATION:
                print("var1", var, response.type)
                error = f'All the variables defined in survey are not available in form or spec'
        return error


def check_and_get_from_spec(key, spec):
        bKey = False
        val = spec.get(key, None)
        if val is not None:
            bKey = True
        return bKey, val


def check_Key(dict, key):
        if key in dict.keys():
            return True
        else:
            return False 