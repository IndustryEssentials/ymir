package constants

type QueryAssetsResult struct {
	AssetsDetail     []MirAssetDetail `json:"elements"`
	Offset           int              `json:"offset"`
	Limit            int              `json:"limit"`
	Anchor           int64            `json:"anchor"`
	TotalAssetsCount int64            `json:"total_assets_count"`
}

type QueryDatasetStatsContext struct {
	RequireAssetsHist      bool `json:"require_assets_hist"`
	RequireAnnotationsHist bool `json:"require_annos_hist"`
	CheckIndexOnly         bool `json:"check_index_only"`

	RepoIndexExist bool `json:"repo_index_exist"`
	RepoIndexReady bool `json:"repo_index_ready"`
}

type QueryDatasetStatsResult struct {
	// Assets
	TotalAssetsCount    int64                `json:"total_assets_count"`
	TotalAssetsFileSize int64                `json:"total_assets_mbytes"`
	AssetsHist          *map[string]*MirHist `json:"assets_hist"`

	// Annotations
	Gt   DatasetStatsElement `json:"gt"`
	Pred DatasetStatsElement `json:"pred"`

	// Cks
	CksCountTotal map[string]int64            `json:"cks_count_total"`
	CksCount      map[string]map[string]int64 `json:"cks_count"`

	// Task and query context.
	NewTypesAdded   bool                     `json:"new_types_added"`
	EvaluationState int                      `json:"evaluation_state"`
	QueryContext    QueryDatasetStatsContext `json:"query_context"`
}

func NewQueryDatasetStatsResult() *QueryDatasetStatsResult {
	queryResult := QueryDatasetStatsResult{
		Gt: DatasetStatsElement{
			ClassIDsCount:    map[int]int64{},
			ClassObjCount:    map[int]int64{},
			TagsCount:        map[string]map[string]int64{},
			TagsCountTotal:   map[string]int64{},
			ClassIDsMaskArea: map[int]int64{},
		},
		Pred: DatasetStatsElement{
			ClassIDsCount:    map[int]int64{},
			ClassObjCount:    map[int]int64{},
			TagsCount:        map[string]map[string]int64{},
			TagsCountTotal:   map[string]int64{},
			ClassIDsMaskArea: map[int]int64{},
		},

		CksCount:      map[string]map[string]int64{},
		CksCountTotal: map[string]int64{},
	}
	return &queryResult
}

type QueryDatasetDupResult struct {
	Duplication   int              `json:"duplication"`
	TotalCount    map[string]int64 `json:"total_count"`
	ResidualCount map[string]int64 `json:"residual_count"`
}
