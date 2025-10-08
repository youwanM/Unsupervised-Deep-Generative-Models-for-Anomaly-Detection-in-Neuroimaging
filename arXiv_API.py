from arxivcollector import ArXivCollector

# Initiate a new instance of the arXivCollector class
collector = ArXivCollector()
# Set the title and type of the exported file
collector.set_title("ArxIv_Results")
collector.set_mode("bibtex")
# Pass the search URL to the run method
collector.run('https://arxiv.org/search/advanced?terms-0-term=Unsupervised&terms-0-operator=AND&terms-0-field=all&terms-1-term=Anomaly&terms-1-operator=AND&terms-1-field=all&terms-2-term=Brain&terms-2-operator=AND&terms-2-field=all&terms-3-term=Deep-learning&terms-3-operator=AND&terms-3-field=all&classification-computer_science=y&classification-physics_archives=all&classification-include_cross_list=include&date-filter_by=all_dates&date-year=&date-from_date=&date-to_date=&date-date_type=submitted_date&abstracts=show&size=200&order=-announced_date_first')