' X Ads API Data Models for EQ12 Integration v3.0
' Complete model definitions for campaign management, analytics, and reporting

Imports System
Imports System.Collections.Generic
Imports System.Text.Json.Serialization

' ==================================================
' ACCOUNT MODELS
' ==================================================

Public Class AdAccount
    <JsonPropertyName("id")>
    Public Property Id As String

    <JsonPropertyName("name")>
    Public Property Name As String

    <JsonPropertyName("business_name")>
    Public Property BusinessName As String

    <JsonPropertyName("timezone")>
    Public Property Timezone As String

    <JsonPropertyName("currency")>
    Public Property Currency As String

    <JsonPropertyName("created_at")>
    Public Property CreatedAt As DateTime

    <JsonPropertyName("updated_at")>
    Public Property UpdatedAt As DateTime

    <JsonPropertyName("deleted")>
    Public Property Deleted As Boolean

    <JsonPropertyName("entity_status")>
    Public Property EntityStatus As String

    <JsonPropertyName("business_id")>
    Public Property BusinessId As String
End Class

Public Class AdAccountDetail
    Inherits AdAccount

    <JsonPropertyName("approval_status")>
    Public Property ApprovalStatus As String

    <JsonPropertyName("funding_instruments")>
    Public Property FundingInstruments As List(Of FundingInstrument)

    <JsonPropertyName("account_media_policy")>
    Public Property AccountMediaPolicy As AccountMediaPolicy

    <JsonPropertyName("features")>
    Public Property Features As List(Of String)
End Class

Public Class FundingInstrument
    <JsonPropertyName("id")>
    Public Property Id As String

    <JsonPropertyName("type")>
    Public Property Type As String

    <JsonPropertyName("currency")>
    Public Property Currency As String

    <JsonPropertyName("credit_limit_local_micro")>
    Public Property CreditLimitLocalMicro As Long?

    <JsonPropertyName("credit_remaining_local_micro")>
    Public Property CreditRemainingLocalMicro As Long?

    <JsonPropertyName("entity_status")>
    Public Property EntityStatus As String

    <JsonPropertyName("io_header")>
    Public Property IoHeader As String
End Class

Public Class AccountMediaPolicy
    <JsonPropertyName("policy_name")>
    Public Property PolicyName As String

    <JsonPropertyName("policy_value")>
    Public Property PolicyValue As String
End Class

' ==================================================
' CAMPAIGN MODELS
' ==================================================

Public Class Campaign
    <JsonPropertyName("id")>
    Public Property Id As String

    <JsonPropertyName("name")>
    Public Property Name As String

    <JsonPropertyName("account_id")>
    Public Property AccountId As String

    <JsonPropertyName("currency")>
    Public Property Currency As String

    <JsonPropertyName("daily_budget_amount_local_micro")>
    Public Property DailyBudgetAmountLocalMicro As Long?

    <JsonPropertyName("total_budget_amount_local_micro")>
    Public Property TotalBudgetAmountLocalMicro As Long?

    <JsonPropertyName("entity_status")>
    Public Property EntityStatus As String

    <JsonPropertyName("start_time")>
    Public Property StartTime As DateTime?

    <JsonPropertyName("end_time")>
    Public Property EndTime As DateTime?

    <JsonPropertyName("created_at")>
    Public Property CreatedAt As DateTime

    <JsonPropertyName("updated_at")>
    Public Property UpdatedAt As DateTime

    <JsonPropertyName("deleted")>
    Public Property Deleted As Boolean

    <JsonPropertyName("funding_instrument_id")>
    Public Property FundingInstrumentId As String

    <JsonPropertyName("reasons_not_servable")>
    Public Property ReasonsNotServable As List(Of String)

    <JsonPropertyName("servable")>
    Public Property Servable As Boolean

    <JsonPropertyName("purchase_order_number")>
    Public Property PurchaseOrderNumber As String
End Class

Public Class CreateCampaignRequest
    <JsonPropertyName("account_id")>
    Public Property AccountId As String

    <JsonPropertyName("name")>
    Public Property Name As String

    <JsonPropertyName("currency")>
    Public Property Currency As String

    <JsonPropertyName("daily_budget_amount_local_micro")>
    Public Property DailyBudgetAmountLocalMicro As Long

    <JsonPropertyName("total_budget_amount_local_micro")>
    Public Property TotalBudgetAmountLocalMicro As Long?

    <JsonPropertyName("entity_status")>
    Public Property EntityStatus As String

    <JsonPropertyName("start_time")>
    Public Property StartTime As DateTime?

    <JsonPropertyName("end_time")>
    Public Property EndTime As DateTime?

    <JsonPropertyName("funding_instrument_id")>
    Public Property FundingInstrumentId As String

    <JsonPropertyName("purchase_order_number")>
    Public Property PurchaseOrderNumber As String
End Class

Public Class UpdateCampaignRequest
    <JsonPropertyName("account_id")>
    Public Property AccountId As String

    <JsonPropertyName("name")>
    Public Property Name As String

    <JsonPropertyName("daily_budget_amount_local_micro")>
    Public Property DailyBudgetAmountLocalMicro As Long?

    <JsonPropertyName("total_budget_amount_local_micro")>
    Public Property TotalBudgetAmountLocalMicro As Long?

    <JsonPropertyName("entity_status")>
    Public Property EntityStatus As String

    <JsonPropertyName("end_time")>
    Public Property EndTime As DateTime?
End Class

' ==================================================
' LINE ITEM (AD GROUP) MODELS
' ==================================================

Public Class LineItem
    <JsonPropertyName("id")>
    Public Property Id As String

    <JsonPropertyName("name")>
    Public Property Name As String

    <JsonPropertyName("campaign_id")>
    Public Property CampaignId As String

    <JsonPropertyName("account_id")>
    Public Property AccountId As String

    <JsonPropertyName("product_type")>
    Public Property ProductType As String

    <JsonPropertyName("objective")>
    Public Property Objective As String

    <JsonPropertyName("entity_status")>
    Public Property EntityStatus As String

    <JsonPropertyName("bid_amount_local_micro")>
    Public Property BidAmountLocalMicro As Long

    <JsonPropertyName("bid_type")>
    Public Property BidType As String

    <JsonPropertyName("automatically_select_bid")>
    Public Property AutomaticallySelectBid As Boolean

    <JsonPropertyName("charge_by")>
    Public Property ChargeBy As String

    <JsonPropertyName("bid_unit")>
    Public Property BidUnit As String

    <JsonPropertyName("advertiser_domain")>
    Public Property AdvertiserDomain As String

    <JsonPropertyName("categories")>
    Public Property Categories As List(Of String)

    <JsonPropertyName("created_at")>
    Public Property CreatedAt As DateTime

    <JsonPropertyName("updated_at")>
    Public Property UpdatedAt As DateTime

    <JsonPropertyName("deleted")>
    Public Property Deleted As Boolean

    <JsonPropertyName("target_cpa_local_micro")>
    Public Property TargetCpaLocalMicro As Long?

    <JsonPropertyName("optimization")>
    Public Property Optimization As String
End Class

Public Class CreateLineItemRequest
    <JsonPropertyName("account_id")>
    Public Property AccountId As String

    <JsonPropertyName("campaign_id")>
    Public Property CampaignId As String

    <JsonPropertyName("name")>
    Public Property Name As String

    <JsonPropertyName("product_type")>
    Public Property ProductType As String

    <JsonPropertyName("objective")>
    Public Property Objective As String

    <JsonPropertyName("entity_status")>
    Public Property EntityStatus As String

    <JsonPropertyName("bid_amount_local_micro")>
    Public Property BidAmountLocalMicro As Long

    <JsonPropertyName("bid_type")>
    Public Property BidType As String

    <JsonPropertyName("automatically_select_bid")>
    Public Property AutomaticallySelectBid As Boolean

    <JsonPropertyName("charge_by")>
    Public Property ChargeBy As String

    <JsonPropertyName("bid_unit")>
    Public Property BidUnit As String

    <JsonPropertyName("advertiser_domain")>
    Public Property AdvertiserDomain As String

    <JsonPropertyName("categories")>
    Public Property Categories As List(Of String)

    <JsonPropertyName("target_cpa_local_micro")>
    Public Property TargetCpaLocalMicro As Long?

    <JsonPropertyName("optimization")>
    Public Property Optimization As String
End Class

' ==================================================
' CREATIVE MODELS
' ==================================================

Public Class MediaCreative
    <JsonPropertyName("id")>
    Public Property Id As String

    <JsonPropertyName("name")>
    Public Property Name As String

    <JsonPropertyName("account_id")>
    Public Property AccountId As String

    <JsonPropertyName("creative_type")>
    Public Property CreativeType As String

    <JsonPropertyName("entity_status")>
    Public Property EntityStatus As String

    <JsonPropertyName("created_at")>
    Public Property CreatedAt As DateTime

    <JsonPropertyName("updated_at")>
    Public Property UpdatedAt As DateTime

    <JsonPropertyName("deleted")>
    Public Property Deleted As Boolean

    <JsonPropertyName("media_key")>
    Public Property MediaKey As String

    <JsonPropertyName("landing_url")>
    Public Property LandingUrl As String

    <JsonPropertyName("approval_status")>
    Public Property ApprovalStatus As String
End Class

Public Class CreateCreativeRequest
    <JsonPropertyName("account_id")>
    Public Property AccountId As String

    <JsonPropertyName("name")>
    Public Property Name As String

    <JsonPropertyName("creative_type")>
    Public Property CreativeType As String

    <JsonPropertyName("entity_status")>
    Public Property EntityStatus As String

    <JsonPropertyName("media_key")>
    Public Property MediaKey As String

    <JsonPropertyName("landing_url")>
    Public Property LandingUrl As String
End Class

Public Class PromotedTweet
    <JsonPropertyName("id")>
    Public Property Id As String

    <JsonPropertyName("account_id")>
    Public Property AccountId As String

    <JsonPropertyName("tweet_id")>
    Public Property TweetId As String

    <JsonPropertyName("entity_status")>
    Public Property EntityStatus As String

    <JsonPropertyName("created_at")>
    Public Property CreatedAt As DateTime

    <JsonPropertyName("updated_at")>
    Public Property UpdatedAt As DateTime

    <JsonPropertyName("deleted")>
    Public Property Deleted As Boolean

    <JsonPropertyName("approval_status")>
    Public Property ApprovalStatus As String
End Class

Public Class CreatePromotedTweetRequest
    <JsonPropertyName("account_id")>
    Public Property AccountId As String

    <JsonPropertyName("tweet_id")>
    Public Property TweetId As String

    <JsonPropertyName("entity_status")>
    Public Property EntityStatus As String = "PAUSED"
End Class

Public Class MediaUploadResponse
    <JsonPropertyName("media_id")>
    Public Property MediaId As String

    <JsonPropertyName("media_key")>
    Public Property MediaKey As String

    <JsonPropertyName("size")>
    Public Property Size As Long

    <JsonPropertyName("expires_after_secs")>
    Public Property ExpiresAfterSecs As Long

    <JsonPropertyName("processing_info")>
    Public Property ProcessingInfo As MediaProcessingInfo
End Class

Public Class MediaProcessingInfo
    <JsonPropertyName("state")>
    Public Property State As String

    <JsonPropertyName("check_after_secs")>
    Public Property CheckAfterSecs As Long?

    <JsonPropertyName("progress_percent")>
    Public Property ProgressPercent As Integer?

    <JsonPropertyName("error")>
    Public Property ErrorInfo As MediaProcessingError
End Class

Public Class MediaProcessingError
    <JsonPropertyName("code")>
    Public Property Code As Integer

    <JsonPropertyName("name")>
    Public Property Name As String

    <JsonPropertyName("message")>
    Public Property Message As String
End Class

' ==================================================
' AUDIENCE MODELS
' ==================================================

Public Class TailoredAudience
    <JsonPropertyName("id")>
    Public Property Id As String

    <JsonPropertyName("name")>
    Public Property Name As String

    <JsonPropertyName("account_id")>
    Public Property AccountId As String

    <JsonPropertyName("list_type")>
    Public Property ListType As String

    <JsonPropertyName("audience_type")>
    Public Property AudienceType As String

    <JsonPropertyName("audience_size")>
    Public Property AudienceSize As Long?

    <JsonPropertyName("created_at")>
    Public Property CreatedAt As DateTime

    <JsonPropertyName("updated_at")>
    Public Property UpdatedAt As DateTime

    <JsonPropertyName("deleted")>
    Public Property Deleted As Boolean

    <JsonPropertyName("is_owner")>
    Public Property IsOwner As Boolean

    <JsonPropertyName("permission_level")>
    Public Property PermissionLevel As String

    <JsonPropertyName("reasons_not_targetable")>
    Public Property ReasonsNotTargetable As List(Of String)

    <JsonPropertyName("targetable")>
    Public Property Targetable As Boolean

    <JsonPropertyName("targetable_types")>
    Public Property TargetableTypes As List(Of String)
End Class

Public Class CreateTailoredAudienceRequest
    <JsonPropertyName("account_id")>
    Public Property AccountId As String

    <JsonPropertyName("name")>
    Public Property Name As String

    <JsonPropertyName("list_type")>
    Public Property ListType As String

    <JsonPropertyName("audience_type")>
    Public Property AudienceType As String = "CUSTOM"
End Class

Public Class AudienceUserUploadRequest
    <JsonPropertyName("users")>
    Public Property Users As List(Of String)

    <JsonPropertyName("user_type")>
    Public Property UserType As String ' EMAIL, PHONE, TWITTER_ID, etc.

    <JsonPropertyName("operation_type")>
    Public Property OperationType As String = "UPDATE"
End Class

' ==================================================
' ANALYTICS AND STATS MODELS
' ==================================================

Public Class StatsJob
    <JsonPropertyName("id")>
    Public Property Id As String

    <JsonPropertyName("status")>
    Public Property Status As String

    <JsonPropertyName("created_at")>
    Public Property CreatedAt As DateTime

    <JsonPropertyName("url")>
    Public Property Url As String

    <JsonPropertyName("expires_at")>
    Public Property ExpiresAt As DateTime?
End Class

Public Class CreateStatsJobRequest
    <JsonPropertyName("account_id")>
    Public Property AccountId As String

    <JsonPropertyName("entity_ids")>
    Public Property EntityIds As List(Of String)

    <JsonPropertyName("entity_type")>
    Public Property EntityType As String ' CAMPAIGN, LINE_ITEM, PROMOTED_TWEET, etc.

    <JsonPropertyName("start_time")>
    Public Property StartTime As DateTime

    <JsonPropertyName("end_time")>
    Public Property EndTime As DateTime

    <JsonPropertyName("granularity")>
    Public Property Granularity As String = "DAY" ' HOUR, DAY, TOTAL

    <JsonPropertyName("metric_groups")>
    Public Property MetricGroups As List(Of String)

    <JsonPropertyName("placement")>
    Public Property Placement As String = "ALL_ON_TWITTER"

    <JsonPropertyName("segmentation_type")>
    Public Property SegmentationType As String

    <JsonPropertyName("platform")>
    Public Property Platform As String
End Class

Public Class StatsJobResult
    <JsonPropertyName("id")>
    Public Property Id As String

    <JsonPropertyName("job_status")>
    Public Property JobStatus As String

    <JsonPropertyName("created_at")>
    Public Property CreatedAt As DateTime

    <JsonPropertyName("start_date")>
    Public Property StartDate As DateTime

    <JsonPropertyName("end_date")>
    Public Property EndDate As DateTime

    <JsonPropertyName("entity_type")>
    Public Property EntityType As String

    <JsonPropertyName("data")>
    Public Property Data As List(Of StatsData)
End Class

Public Class StatsData
    <JsonPropertyName("id")>
    Public Property Id As String

    <JsonPropertyName("id_data")>
    Public Property IdData As List(Of EntityIdData)

    <JsonPropertyName("metrics")>
    Public Property Metrics As StatsMetrics
End Class

Public Class EntityIdData
    <JsonPropertyName("entity_id")>
    Public Property EntityId As String

    <JsonPropertyName("entity_type")>
    Public Property EntityType As String
End Class

Public Class StatsMetrics
    <JsonPropertyName("impressions")>
    Public Property Impressions As Long

    <JsonPropertyName("engagements")>
    Public Property Engagements As Long

    <JsonPropertyName("engagement_rate")>
    Public Property EngagementRate As Double

    <JsonPropertyName("retweets")>
    Public Property Retweets As Long

    <JsonPropertyName("replies")>
    Public Property Replies As Long

    <JsonPropertyName("likes")>
    Public Property Likes As Long

    <JsonPropertyName("follows")>
    Public Property Follows As Long

    <JsonPropertyName("clicks")>
    Public Property Clicks As Long

    <JsonPropertyName("url_clicks")>
    Public Property UrlClicks As Long

    <JsonPropertyName("profile_clicks")>
    Public Property ProfileClicks As Long

    <JsonPropertyName("video_total_views")>
    Public Property VideoTotalViews As Long

    <JsonPropertyName("video_views_25")>
    Public Property VideoViews25 As Long

    <JsonPropertyName("video_views_50")>
    Public Property VideoViews50 As Long

    <JsonPropertyName("video_views_75")>
    Public Property VideoViews75 As Long

    <JsonPropertyName("video_views_100")>
    Public Property VideoViews100 As Long

    <JsonPropertyName("billed_charge_local_micro")>
    Public Property BilledChargeLocalMicro As Long

    <JsonPropertyName("billed_engagements")>
    Public Property BilledEngagements As Long

    <JsonPropertyName("qualified_impressions")>
    Public Property QualifiedImpressions As Long

    <JsonPropertyName("app_clicks")>
    Public Property AppClicks As Long

    <JsonPropertyName("app_installs")>
    Public Property AppInstalls As Long

    <JsonPropertyName("conversion_purchases")>
    Public Property ConversionPurchases As Long

    <JsonPropertyName("conversion_sign_ups")>
    Public Property ConversionSignUps As Long

    <JsonPropertyName("conversion_site_visits")>
    Public Property ConversionSiteVisits As Long

    <JsonPropertyName("conversion_downloads")>
    Public Property ConversionDownloads As Long

    <JsonPropertyName("conversion_custom")>
    Public Property ConversionCustom As Long
End Class

' ==================================================
' EQ12 SPECIFIC ANALYTICS MODELS
' ==================================================

Public Class CampaignAnalytics
    Public Property CampaignId As String
    Public Property CampaignName As String
    Public Property CampaignStatus As String
    Public Property AccountId As String
    Public Property StartDate As DateTime
    Public Property EndDate As DateTime
    Public Property Currency As String
    Public Property DailyBudgetAmountLocalMicro As Long?

    ' Core Metrics
    Public Property TotalImpressions As Long
    Public Property TotalEngagements As Long
    Public Property TotalSpend As Decimal
    Public Property EngagementRate As Double
    Public Property CPM As Double
    Public Property CostPerEngagement As Double

    ' Detailed Engagement Metrics
    Public Property TotalRetweets As Long
    Public Property TotalReplies As Long
    Public Property TotalLikes As Long
    Public Property TotalFollows As Long
    Public Property TotalClicks As Long
    Public Property TotalUrlClicks As Long
    Public Property TotalProfileClicks As Long

    ' Video Metrics
    Public Property VideoTotalViews As Long
    Public Property VideoViews25 As Long
    Public Property VideoViews50 As Long
    Public Property VideoViews75 As Long
    Public Property VideoViews100 As Long
    Public Property VideoCompletionRate As Double

    ' Conversion Metrics
    Public Property TotalConversions As Long
    Public Property ConversionRate As Double
    Public Property CostPerConversion As Double

    ' EQ12 Enhanced Metrics
    Public Property EQ12EngagementScore As Double
    Public Property EQ12ROI As Double
    Public Property EQ12ViralityScore As Double
    Public Property EQ12QualityScore As Double

    ' Comparative Metrics
    Public Property BenchmarkEngagementRate As Double
    Public Property PerformanceIndex As Double
    Public Property TrendDirection As String ' UP, DOWN, STABLE

    ' Attribution
    Public Property GeneratedAt As DateTime
    Public Property DataSource As String = "X_Ads_API"
End Class

' ==================================================
' RESPONSE WRAPPERS
' ==================================================

Public Class AdAccountsResponse
    <JsonPropertyName("data")>
    Public Property Data As List(Of AdAccount)

    <JsonPropertyName("request")>
    Public Property Request As RequestInfo
End Class

Public Class AdAccountDetailResponse
    <JsonPropertyName("data")>
    Public Property Data As AdAccountDetail

    <JsonPropertyName("request")>
    Public Property Request As RequestInfo
End Class

Public Class CampaignResponse
    <JsonPropertyName("data")>
    Public Property Data As Campaign

    <JsonPropertyName("request")>
    Public Property Request As RequestInfo
End Class

Public Class CampaignsResponse
    <JsonPropertyName("data")>
    Public Property Data As List(Of Campaign)

    <JsonPropertyName("request")>
    Public Property Request As RequestInfo
End Class

Public Class LineItemResponse
    <JsonPropertyName("data")>
    Public Property Data As LineItem

    <JsonPropertyName("request")>
    Public Property Request As RequestInfo
End Class

Public Class CreativeResponse
    <JsonPropertyName("data")>
    Public Property Data As MediaCreative

    <JsonPropertyName("request")>
    Public Property Request As RequestInfo
End Class

Public Class PromotedTweetResponse
    <JsonPropertyName("data")>
    Public Property Data As PromotedTweet

    <JsonPropertyName("request")>
    Public Property Request As RequestInfo
End Class

Public Class TailoredAudienceResponse
    <JsonPropertyName("data")>
    Public Property Data As TailoredAudience

    <JsonPropertyName("request")>
    Public Property Request As RequestInfo
End Class

Public Class FundingInstrumentsResponse
    <JsonPropertyName("data")>
    Public Property Data As List(Of FundingInstrument)

    <JsonPropertyName("request")>
    Public Property Request As RequestInfo
End Class

Public Class StatsJobResponse
    <JsonPropertyName("data")>
    Public Property Data As StatsJob

    <JsonPropertyName("request")>
    Public Property Request As RequestInfo
End Class

' ==================================================
' HELPER MODELS
' ==================================================

Public Class RequestInfo
    <JsonPropertyName("params")>
    Public Property Params As Dictionary(Of String, Object)

    <JsonPropertyName("request_id")>
    Public Property RequestId As String

    <JsonPropertyName("method")>
    Public Property Method As String

    <JsonPropertyName("url")>
    Public Property Url As String
End Class

Public Class BitlyConfig
    Public Property AccessToken As String
    Public Property GroupId As String
End Class

Public Class EQ12AdCampaignTemplate
    Public Property Name As String
    Public Property Objective As String
    Public Property BudgetType As String ' DAILY, LIFETIME
    Public Property BudgetAmount As Decimal
    Public Property TargetAudience As String
    Public Property AdFormat As String
    Public Property DurationDays As Integer
    Public Property AutoOptimization As Boolean = True
    Public Property EQ12Tags As List(Of String)
End Class

Public Class EQ12AutoPromotionRule
    Public Property Id As String
    Public Property Name As String
    Public Property TriggerConditions As Dictionary(Of String, Object)
    Public Property PromotionBudget As Decimal
    Public Property MaxDailyPromotions As Integer
    Public Property IsActive As Boolean
    Public Property CreatedAt As DateTime
    Public Property UpdatedAt As DateTime
End Class
