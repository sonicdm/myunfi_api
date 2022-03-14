from threading import Thread
from typing import TYPE_CHECKING, Dict, List, Union
import tkinter as tk
import tkinter.ttk as ttk
from unfi_api.utils import threading
from unfi_api.utils.jobs import Job, Jobs
from .settings import thread_type
if TYPE_CHECKING:
    from model import TkModel
    from view import View
    from container import TkContainer


class Controller:
    def __init__(self, title, container: "TkContainer", model: "TkModel" = None):
        self.title = title
        self.model: "TkModel" = model(self)
        self.container: "TkContainer" = container(self, title)
        self.home_frame: str = None
        self.models: dict[str, TkModel] = {}
        self.ready: bool = False
        self.cancel = []
        self.cancel_all = False
        self.thread_pool: Dict[str, Thread] = {}
        self.jobs = Jobs()

    def register_views(self, frames: List["View"]) -> None:
        self.container.setup(frames)
        self.setup = True

    def show_view(self, name: str, model_name: str = None) -> None:
        self.container.show_view(name)

    def show_main_view(self) -> None:
        self.container.show_main_view()

    def register_view(self, view: "View") -> None:
        if not view.model:
            view.model = self.model
        self.container.register_view(view)
        self.ready = True

    def register_main_view(self, view: "View") -> None:
        self.container.register_main_view(view)

    def destroy_view(self):
        self.container.destroy()

    def get_tk_variable(self, name: str, model_name: str = None) -> tk.Variable:
        if model_name in self.models:
            return self.models[model_name].get_tk_variable(name)
        return self.model.get_tk_variable(name)

    def store_tk_variable(self, name: str, value: str, model_name: str = None) -> None:
        if model_name in self.models:
            self.models[model_name].store_tk_variable(name, value)
        else:
            self.model.store_tk_variable(name, value)

    def get_variable_value(self, name: str, model_name: str = None) -> str:
        if model_name in self.models:
            return self.models[model_name].get_variable_value(name)
        return self.model.get_variable_value(name)

    def set_variable_value(self, name: str, value: str, model_name: str = None) -> None:
        if model_name in self.models:
            self.models[model_name].set_variable_value(name, value)
        else:
            self.model.set_variable_value(name, value)

    def run(self) -> None:
        if not self.ready:
            raise Exception("Controller not setup and ready to launch")

        self.container.run()

    def quit(self) -> None:
        self.container.destroy()

    def setup(self) -> None:
        ...

    def set_job_status(self, job_id, status: str) -> None:
        self.jobs.set_job_status(job_id, status)

    def cancel_job(self, job_id: str) -> None:
        self.jobs.cancel_job(job_id)
        return self.jobs.get_job_status(job_id)

    def cancel_all_jobs(self) -> None:
        for job in self.jobs.get_jobs().values():
            job.cancel()

    def finish_job(self, job_id: str) -> None:
        self.jobs.set_job_status(job_id, "finished")

    def get_job_status(self, job_id: str) -> str:
        if job_id in self.jobs:
            return self.jobs.get_job_status(job_id)

    def create_job(
        self,
        job_id,
        job_fn,
        job_data,
        job_args=None,
        job_kwargs=None,
        callback=None,
        threaded=False,
        executor_options=None,
        executor=None,
        suppress_errors=False,
        thread_type=thread_type,
    ) -> Job:
        job = self.jobs.create_job(
            job_id,
            job_fn,
            job_data,
            job_args=job_args,
            job_kwargs=job_kwargs,
            callback=callback,
            threaded=threaded,
            executor_options=executor_options,
            executor=executor,
            suppress_errors=suppress_errors,
            thread_type=thread_type,
        )
        return job


    def show_message(self, message_type, message: str, title: str = "Message") -> None:
        self.container.show_message(message_type, title, message)
