"""Provide summary statistics on data."""
from plugin import Statistics
from numpy import min, max, mean, median, std

class Summary(Statistics):
    """Plugin to display summary statistics"""
    name = "Summary"
    def Main(self, model):
        """Calculate summary statistics"""
        self.model = model
        fields = self.model.GetCurrentData().getAttr('fields')
        data = self.model.GetCurrentData()[:]
        low = list(min(data, axis=0))
        high = list(max(data, axis=0))
        mu = list(mean(data, axis=0))
        med = list(median(data))
        sig = list(std(data, axis=0))
        
        self.model.NewGroup('Summary statistics')
        self.model.hdf5.createArray(self.model.current_group, 'min', low)
        self.model.hdf5.createArray(self.model.current_group, 'max', high)
        self.model.hdf5.createArray(self.model.current_group, 'mean', mu)
        self.model.hdf5.createArray(self.model.current_group, 'median', med)
        self.model.hdf5.createArray(self.model.current_group, 'stdev', sig)
        self.model.update()
