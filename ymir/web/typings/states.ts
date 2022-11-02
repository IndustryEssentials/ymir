declare namespace YStates {
  type ResultCache<T> = { [key: string | number]: T }
  type DatasetState = {
    dataset: {
      dataset: ResultCache<YModels.Dataset>
    }
  }
  type ModelState = {
    model: {
      model: ResultCache<YModels.Model>,
    }
  }
}