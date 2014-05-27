from plugin import Statistics
import numpy

class Mean(Statistics):
  """Calculate channel averages and append statistic to group."""
  name = 'Average'

  def Main(self, model):
    """Retrieve column data from Model and attach calculated column means."""

    # make a copy of the currently selected group's data
    data = model.GetCurrentData()[:]

    # calculate the mean per channel
    avg = numpy.mean(data, axis=0)

    # make a new array to store the calculated means
    model.NewArray('average', avg)
