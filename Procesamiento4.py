from mrjob.job import MRJob
from mrjob.step import MRStep

class Repuestos(MRJob):
    def steps(self):
       return [
            MRStep(mapper=self.mapper_get_ratings,
                   reducer=self.reducer_count_ratings)
        ]

    def mapper_get_ratings(self, _, line):
        (id_orden,id_proveedor,fecha_pedido,estado) = line.split("\t")
        yield estado,1

    def reducer_count_ratings(self, key, values):
        yield key, sum(values)

if __name__ == '__main__':
    Repuestos.run()
