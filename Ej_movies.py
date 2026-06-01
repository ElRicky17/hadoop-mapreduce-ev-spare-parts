from mrjob.job import MRJob
from mrjob.step import MRStep

class Movies(MRJob):
    def steps(self):
        return [
            MRStep(mapper=self.mapper_get_ratings,
                   reducer=self.reducer_count_ratings),
            MRStep(reducer=self.reducer_sort_ratings) 
        ]

    def mapper_get_ratings(self, _, line):
        (user_id, movie_id, rating, timestamp) = line.split("\t")
        yield movie_id, int(rating)

    def reducer_count_ratings(self, movie_id, values):
        yield None, (sum(values), movie_id)

    def reducer_sort_ratings(self, _, total_movie_pairs):
        for total, movie_id in sorted(total_movie_pairs, reverse=True):
            yield movie_id, total

if __name__ == '__main__':
    Movies.run()
