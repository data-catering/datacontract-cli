from datetime import datetime as dt

from pyscript import document, window
from pyweb import pydom

from datacontract.lint import resolve
from datacontract.lint.files import read_file
from datacontract.export.exporter_factory import exporter_factory

tasks = []


def q(selector, root=document):
    return root.querySelector(selector)


# define the task template that will be used to render new templates to the page
# Note: We use JS element here because pydom doesn't fully support template
#       elements now
task_template = pydom.Element(q("#task-template").content.querySelector(".task"))

task_list = pydom["#list-tasks-container"][0]
new_task_content = pydom["#new-task-content"][0]

output_type = pydom["#convert-output-type"][0]
ace = window.ace
ace.require("ace/ext/language_tools")
editor_input = ace.edit("input-yaml")
editor_output = ace.edit("output-text")

provider = window.LanguageProvider.fromCdn("https://cdn.jsdelivr.net/npm/ace-linters/build")


def add_task(e):
    # ignore empty task
    if not new_task_content.value:
        return None

    # create task
    task_id = f"task-{len(tasks)}"
    task = {
        "id": task_id,
        "content": new_task_content.value,
        "done": False,
        "created_at": dt.now(),
    }

    tasks.append(task)

    # add the task element to the page as new node in the list by cloning from a
    # template
    task_html = task_template.clone()
    task_html.id = task_id

    task_html_check = task_html.find("input")[0]
    task_html_content = task_html.find("p")[0]
    task_html_content._js.textContent = task["content"]
    task_list.append(task_html)

    def check_task(evt=None):
        task["done"] = not task["done"]
        task_html_content._js.classList.toggle("line-through", task["done"])

    new_task_content.value = ""
    task_html_check._js.onclick = check_task


def add_task_event(e):
    if e.key == "Enter":
        add_task(e)


def init_ace_editor():
    setup_editor(editor_input)
    setup_editor(editor_output)
    example_input = read_file("datacontract/pyscript/example/data-contract-specification.yaml")
    editor_input.setValue(example_input)


def setup_editor(editor):
    editor.session.setMode("ace/mode/yaml")
    editor.setTheme("ace/theme/chrome")
    editor.setOptions({
        "autoScrollEditorIntoView": True,
        "customScrollbar": True,
        "enableAutoIndent": True,
        "enableBasicAutocompletion": True,
        "enableSnippets": True,
        "enableLiveAutocompletion": True,
        "minLines": 100,
        "useWorker": False,
        "wrap": True
    })


def export_to_output_type(e):
    data_contract = resolve.resolve_data_contract(data_contract_str=editor_input.getValue())
    export_result = exporter_factory.create(output_type.value).export(
        data_contract=data_contract,
        model="all",
        server=None,
        sql_server_type="auto",
        export_args={}
    )
    editor_output.session.setValue(export_result)


new_task_content.onkeypress = add_task_event
init_ace_editor()
