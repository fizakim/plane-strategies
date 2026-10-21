import argparse
import os
from dataclasses import dataclass
from datetime import date

from dotenv import load_dotenv

from .config import BLOCKS, SCHEDULE, SETTINGS
from .models import FlightQuery
from .serpapi_source import SerpApiError, SerpApiSource
from .store import Store


@dataclass
class Job:
    block: object
    depart_date: date
    lead_days: int


class Collector:
    def __init__(self, source, store, blocks, schedule, settings):
        self.source = source
        self.store = store
        self.blocks = blocks
        self.schedule = schedule
        self.settings = settings

    def plan(self, today):
        jobs = []
        for depart_date, lead in self.schedule.departures(today):
            for block in self.blocks:
                if not self.store.already_done(block.name, depart_date.isoformat(), today.isoformat()):
                    jobs.append(Job(block, depart_date, lead))
        return jobs

    def run(self, today=None, dry_run=False):
        today = today or date.today()
        jobs = self.plan(today)
        if not jobs:
            print(today, "- nothing to collect")
            return
        print(today, "-", len(jobs), "calls planned")

        if dry_run:
            for job in jobs:
                print(" ", job.block.name, "departs", job.depart_date, "(" + str(job.lead_days) + " days out)")
            return

        left = self.source.credits_left() - self.settings.reserve
        if left < len(jobs):
            print("only", left, "credits to spend, running the first", max(left, 0), "of", len(jobs))
            jobs = jobs[:max(left, 0)]

        fails = 0
        for job in jobs:
            if self.run_job(job, today):
                fails = 0
            else:
                fails += 1
            if fails >= self.settings.max_errors:
                print("stopping,", fails, "failed calls in a row")
                break

    def run_job(self, job, today):
        query = FlightQuery(self.settings.airlines, job.block.origins, job.block.dests,
                            job.depart_date.isoformat())
        params = self.source.params(query)
        data = None
        error = None
        fares = []
        try:
            data = self.source.raw(query)
            if "error" in data:
                error = data["error"]
            else:
                fares = self.source.parse(data)
        except SerpApiError as e:
            error = str(e)

        self.store.save(job.block.name, query.date, job.lead_days, today.isoformat(),
                        params, data, error, fares)
        if error:
            print(" ", job.block.name, query.date, "ERROR", error)
        else:
            print(" ", job.block.name, query.date, len(fares), "flights")
        return error is None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    load_dotenv()
    source = SerpApiSource(os.environ.get("SERPAPI_KEY"), SETTINGS.currency, SETTINGS.gl, SETTINGS.hl)
    collector = Collector(source, Store(SETTINGS.data_dir), BLOCKS, SCHEDULE, SETTINGS)
    collector.run(dry_run=args.dry_run)


if __name__ == "__main__":
    main()
