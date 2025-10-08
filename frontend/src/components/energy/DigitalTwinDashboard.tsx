/**
 * DigitalTwinDashboard Component
 * Comprehensive dashboard displaying digital twin energy insights
 */

import React, { useEffect } from 'react';
import {
  IonPage,
  IonHeader,
  IonToolbar,
  IonTitle,
  IonContent,
  IonRefresher,
  IonRefresherContent,
  IonGrid,
  IonRow,
  IonCol,
  IonCard,
  IonCardHeader,
  IonCardTitle,
  IonCardContent,
  IonChip,
  IonIcon,
  IonSpinner,
  RefresherEventDetail,
} from '@ionic/react';
import {
  flashOutline,
  trendingUpOutline,
  statsChartOutline,
  timeOutline,
} from 'ionicons/icons';
import useEnergyStore from '../../store/energyStore';
import EnergyPredictionCard from './EnergyPredictionCard';
import EnergyCurveChart from './EnergyCurveChart';

const DigitalTwinDashboard: React.FC = () => {
  const {
    digitalTwin,
    futurePredictions,
    modelAccuracy,
    isLoading,
    error,
    fetchDigitalTwin,
    fetchFuturePredictions,
    fetchModelAccuracy,
    clearError,
  } = useEnergyStore();

  // 初始加载数据
  useEffect(() => {
    fetchDigitalTwin();
    fetchFuturePredictions(24); // 获取未来24小时预测
    fetchModelAccuracy();
  }, []);

  // 下拉刷新
  const handleRefresh = async (event: CustomEvent<RefresherEventDetail>) => {
    await Promise.all([
      fetchDigitalTwin(),
      fetchFuturePredictions(24),
      fetchModelAccuracy(),
    ]);
    event.detail.complete();
  };

  // 格式化百分比
  const formatPercentage = (value: number) => {
    return `${(value * 100).toFixed(1)}%`;
  };

  // 格式化时间
  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleString('zh-CN', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <IonPage>
      <IonHeader>
        <IonToolbar>
          <IonTitle>精力数字孪生</IonTitle>
        </IonToolbar>
      </IonHeader>

      <IonContent fullscreen>
        <IonRefresher slot="fixed" onIonRefresh={handleRefresh}>
          <IonRefresherContent />
        </IonRefresher>

        {error && (
          <IonCard color="danger" className="m-4">
            <IonCardContent>
              <p className="text-white">{error}</p>
              <button
                className="text-white underline mt-2"
                onClick={clearError}
              >
                关闭
              </button>
            </IonCardContent>
          </IonCard>
        )}

        <IonGrid>
          <IonRow>
            <IonCol size="12">
              {/* 当前精力状态卡片 */}
              <EnergyPredictionCard
                prediction={digitalTwin?.current_energy || null}
                isLoading={isLoading}
              />
            </IonCol>
          </IonRow>

          <IonRow>
            <IonCol size="12">
              {/* 24小时精力趋势图 */}
              <EnergyCurveChart
                predictions={futurePredictions}
                isLoading={isLoading}
                title="未来24小时精力预测"
              />
            </IonCol>
          </IonRow>

          {/* 数字孪生统计信息 */}
          {digitalTwin && (
            <>
              <IonRow>
                <IonCol size="12">
                  <IonCard>
                    <IonCardHeader>
                      <IonCardTitle className="flex items-center">
                        <IonIcon icon={statsChartOutline} className="mr-2" />
                        数字孪生统计
                      </IonCardTitle>
                    </IonCardHeader>
                    <IonCardContent>
                      <IonGrid>
                        <IonRow>
                          <IonCol size="6">
                            <div className="text-center p-3 bg-gray-50 rounded-lg">
                              <p className="text-xs text-gray-600 mb-1">数据完整度</p>
                              <p className="text-2xl font-bold text-blue-600">
                                {formatPercentage(digitalTwin.data_completeness)}
                              </p>
                            </div>
                          </IonCol>
                          <IonCol size="6">
                            <div className="text-center p-3 bg-gray-50 rounded-lg">
                              <p className="text-xs text-gray-600 mb-1">模式数量</p>
                              <p className="text-2xl font-bold text-green-600">
                                {digitalTwin.patterns?.length || 0}
                              </p>
                            </div>
                          </IonCol>
                        </IonRow>
                        <IonRow className="mt-3">
                          <IonCol size="6">
                            <div className="text-center p-3 bg-gray-50 rounded-lg">
                              <p className="text-xs text-gray-600 mb-1">总数据点</p>
                              <p className="text-2xl font-bold text-purple-600">
                                {digitalTwin.stats?.total_data_points || 0}
                              </p>
                            </div>
                          </IonCol>
                          <IonCol size="6">
                            <div className="text-center p-3 bg-gray-50 rounded-lg">
                              <p className="text-xs text-gray-600 mb-1">数据天数</p>
                              <p className="text-2xl font-bold text-orange-600">
                                {digitalTwin.stats?.days_of_data || 0}
                              </p>
                            </div>
                          </IonCol>
                        </IonRow>
                      </IonGrid>

                      <div className="mt-4 text-xs text-gray-500 flex items-center justify-end">
                        <IonIcon icon={timeOutline} className="mr-1" />
                        更新时间: {formatTime(digitalTwin.last_updated)}
                      </div>
                    </IonCardContent>
                  </IonCard>
                </IonCol>
              </IonRow>

              {/* 个人基线 */}
              {digitalTwin.baseline && (
                <IonRow>
                  <IonCol size="12">
                    <IonCard>
                      <IonCardHeader>
                        <IonCardTitle className="flex items-center">
                          <IonIcon icon={trendingUpOutline} className="mr-2" />
                          个人精力基线
                        </IonCardTitle>
                      </IonCardHeader>
                      <IonCardContent>
                        <IonGrid>
                          <IonRow>
                            <IonCol size="4">
                              <div className="text-center">
                                <p className="text-xs text-gray-600 mb-1">平均精力</p>
                                <p className="text-xl font-bold">
                                  {digitalTwin.baseline.avg_energy_level.toFixed(1)}
                                </p>
                              </div>
                            </IonCol>
                            <IonCol size="4">
                              <div className="text-center">
                                <p className="text-xs text-gray-600 mb-1">峰值时段</p>
                                <p className="text-xl font-bold">
                                  {digitalTwin.baseline.peak_hours?.[0] || 'N/A'}:00
                                </p>
                              </div>
                            </IonCol>
                            <IonCol size="4">
                              <div className="text-center">
                                <p className="text-xs text-gray-600 mb-1">低谷时段</p>
                                <p className="text-xl font-bold">
                                  {digitalTwin.baseline.low_hours?.[0] || 'N/A'}:00
                                </p>
                              </div>
                            </IonCol>
                          </IonRow>
                        </IonGrid>

                        {digitalTwin.baseline.optimal_activities && (
                          <div className="mt-4">
                            <h4 className="text-sm font-semibold mb-2">最佳活动时段</h4>
                            <div className="flex flex-wrap gap-2">
                              {Object.entries(digitalTwin.baseline.optimal_activities).map(
                                ([activity, hours]) => (
                                  <IonChip key={activity} color="primary" outline>
                                    <span className="text-xs">
                                      {activity}: {Array.isArray(hours) ? hours.join(', ') : hours}
                                    </span>
                                  </IonChip>
                                )
                              )}
                            </div>
                          </div>
                        )}
                      </IonCardContent>
                    </IonCard>
                  </IonCol>
                </IonRow>
              )}

              {/* 精力模式 */}
              {digitalTwin.patterns && digitalTwin.patterns.length > 0 && (
                <IonRow>
                  <IonCol size="12">
                    <IonCard>
                      <IonCardHeader>
                        <IonCardTitle className="flex items-center">
                          <IonIcon icon={flashOutline} className="mr-2" />
                          识别的精力模式
                        </IonCardTitle>
                      </IonCardHeader>
                      <IonCardContent>
                        {digitalTwin.patterns.map((pattern, index) => (
                          <div
                            key={pattern.id || index}
                            className="mb-4 p-3 bg-gray-50 rounded-lg"
                          >
                            <div className="flex justify-between items-center mb-2">
                              <span className="font-semibold">{pattern.pattern_type}</span>
                              <IonChip color="primary">
                                置信度: {formatPercentage(pattern.confidence)}
                              </IonChip>
                            </div>
                            <p className="text-sm text-gray-700">{pattern.description}</p>
                            {pattern.triggers && pattern.triggers.length > 0 && (
                              <div className="mt-2 flex flex-wrap gap-1">
                                {pattern.triggers.map((trigger, idx) => (
                                  <IonChip key={idx} size="small" outline>
                                    <span className="text-xs">{trigger}</span>
                                  </IonChip>
                                ))}
                              </div>
                            )}
                          </div>
                        ))}
                      </IonCardContent>
                    </IonCard>
                  </IonCol>
                </IonRow>
              )}

              {/* AI建议 */}
              {digitalTwin.recommendations && digitalTwin.recommendations.length > 0 && (
                <IonRow>
                  <IonCol size="12">
                    <IonCard>
                      <IonCardHeader>
                        <IonCardTitle className="flex items-center">
                          <IonIcon icon={trendingUpOutline} className="mr-2" />
                          AI优化建议
                        </IonCardTitle>
                      </IonCardHeader>
                      <IonCardContent>
                        <ul className="list-disc list-inside space-y-2">
                          {digitalTwin.recommendations.map((rec, index) => (
                            <li key={index} className="text-sm text-gray-700">
                              {rec}
                            </li>
                          ))}
                        </ul>
                      </IonCardContent>
                    </IonCard>
                  </IonCol>
                </IonRow>
              )}
            </>
          )}

          {/* 模型准确性 */}
          {modelAccuracy && (
            <IonRow>
              <IonCol size="12">
                <IonCard>
                  <IonCardHeader>
                    <IonCardTitle>模型准确性指标</IonCardTitle>
                  </IonCardHeader>
                  <IonCardContent>
                    <IonGrid>
                      <IonRow>
                        <IonCol size="6">
                          <div className="text-center p-3 bg-gray-50 rounded-lg">
                            <p className="text-xs text-gray-600 mb-1">平均误差(MAE)</p>
                            <p className="text-xl font-bold text-blue-600">
                              {modelAccuracy.mae.toFixed(2)}
                            </p>
                          </div>
                        </IonCol>
                        <IonCol size="6">
                          <div className="text-center p-3 bg-gray-50 rounded-lg">
                            <p className="text-xs text-gray-600 mb-1">均方根误差</p>
                            <p className="text-xl font-bold text-green-600">
                              {modelAccuracy.rmse.toFixed(2)}
                            </p>
                          </div>
                        </IonCol>
                      </IonRow>
                      <IonRow className="mt-3">
                        <IonCol size="6">
                          <div className="text-center p-3 bg-gray-50 rounded-lg">
                            <p className="text-xs text-gray-600 mb-1">平均置信度</p>
                            <p className="text-xl font-bold text-purple-600">
                              {formatPercentage(modelAccuracy.avg_confidence)}
                            </p>
                          </div>
                        </IonCol>
                        <IonCol size="6">
                          <div className="text-center p-3 bg-gray-50 rounded-lg">
                            <p className="text-xs text-gray-600 mb-1">验证次数</p>
                            <p className="text-xl font-bold text-orange-600">
                              {modelAccuracy.validation_count}
                            </p>
                          </div>
                        </IonCol>
                      </IonRow>
                    </IonGrid>
                  </IonCardContent>
                </IonCard>
              </IonCol>
            </IonRow>
          )}
        </IonGrid>
      </IonContent>
    </IonPage>
  );
};

export default DigitalTwinDashboard;
