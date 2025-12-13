// eq12_modern_react_dashboard.js
/**
 * EQ12 Modern React Dashboard with Tailwind CSS
 * Real-time betting analytics with beautiful, responsive UI
 */

import {
    BellIcon,
    ChartBarIcon,
    CheckCircleIcon,
    ClockIcon,
    ExclamationTriangleIcon,
    FireIcon,
    LightningBoltIcon,
    TrophyIcon,
    XCircleIcon
} from '@heroicons/react/24/outline';
import { useEffect, useState } from 'react';

// Real-time WebSocket hook
const useWebSocket = (url, options = {}) => {
    const [socket, setSocket] = useState(null);
    const [lastMessage, setLastMessage] = useState(null);
    const [connectionStatus, setConnectionStatus] = useState('Connecting');
    const [messageHistory, setMessageHistory] = useState([]);

    useEffect(() => {
        const ws = new WebSocket(url);

        ws.onopen = () => {
            setConnectionStatus('Connected');
            setSocket(ws);
        };

        ws.onclose = () => {
            setConnectionStatus('Disconnected');
            setSocket(null);
        };

        ws.onmessage = (event) => {
            const message = JSON.parse(event.data);
            setLastMessage(message);
            setMessageHistory(prev => [message, ...prev.slice(0, 99)]); // Keep last 100
        };

        ws.onerror = () => {
            setConnectionStatus('Error');
        };

        return () => {
            ws.close();
        };
    }, [url]);

    const sendMessage = (message) => {
        if (socket && socket.readyState === WebSocket.OPEN) {
            socket.send(JSON.stringify(message));
        }
    };

    return { socket, lastMessage, connectionStatus, messageHistory, sendMessage };
};

// Alert Level Component
const AlertBadge = ({ level }) => {
    const styles = {
        info: 'bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-400',
        warning: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-400',
        critical: 'bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400',
        emergency: 'bg-purple-100 text-purple-800 dark:bg-purple-900/20 dark:text-purple-400'
    };

    const icons = {
        info: CheckCircleIcon,
        warning: ExclamationTriangleIcon,
        critical: XCircleIcon,
        emergency: FireIcon
    };

    const Icon = icons[level] || CheckCircleIcon;

    return (
        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${styles[level]}`}>
            <Icon className="w-3 h-3 mr-1" />
            {level.charAt(0).toUpperCase() + level.slice(1)}
        </span>
    );
};

// Connection Status Indicator
const ConnectionStatus = ({ status }) => {
    const statusStyles = {
        'Connected': 'bg-green-500 text-white',
        'Connecting': 'bg-yellow-500 text-white animate-pulse',
        'Disconnected': 'bg-red-500 text-white',
        'Error': 'bg-red-600 text-white'
    };

    return (
        <div className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${statusStyles[status]}`}>
            <div className="w-2 h-2 bg-white rounded-full mr-2" />
            {status}
        </div>
    );
};

// Health Status Card
const HealthCard = ({ component, health }) => {
    const getStatusColor = (status) => {
        switch (status) {
            case 'healthy': return 'text-green-400 bg-green-900/20';
            case 'degraded': return 'text-yellow-400 bg-yellow-900/20';
            case 'critical': return 'text-red-400 bg-red-900/20';
            default: return 'text-gray-400 bg-gray-900/20';
        }
    };

    const getStatusIcon = (status) => {
        switch (status) {
            case 'healthy': return CheckCircleIcon;
            case 'degraded': return ExclamationTriangleIcon;
            case 'critical': return XCircleIcon;
            default: return ClockIcon;
        }
    };

    const StatusIcon = getStatusIcon(health.status);

    return (
        <div className="bg-gray-800/50 backdrop-blur-sm border border-gray-700 rounded-xl p-6 transition-all hover:border-gray-600">
            <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-white capitalize">
                    {component.replace(/_/g, ' ')}
                </h3>
                <StatusIcon className={`w-6 h-6 ${health.status === 'healthy' ? 'text-green-400' : 'text-yellow-400'}`} />
            </div>

            <div className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium mb-4 ${getStatusColor(health.status)}`}>
                {health.status}
            </div>

            <div className="space-y-2 text-sm text-gray-400">
                <div className="flex justify-between">
                    <span>Response Time</span>
                    <span className="text-white">{health.response_time_ms?.toFixed(1)}ms</span>
                </div>

                {health.details?.cpu_percent && (
                    <div className="flex justify-between">
                        <span>CPU Usage</span>
                        <span className="text-white">{health.details.cpu_percent.toFixed(1)}%</span>
                    </div>
                )}

                {health.details?.memory_percent && (
                    <div className="flex justify-between">
                        <span>Memory Usage</span>
                        <span className="text-white">{health.details.memory_percent.toFixed(1)}%</span>
                    </div>
                )}

                {health.details?.active_connections !== undefined && (
                    <div className="flex justify-between">
                        <span>Connections</span>
                        <span className="text-white">{health.details.active_connections}</span>
                    </div>
                )}
            </div>
        </div>
    );
};

// Real-time Event Card
const EventCard = ({ event }) => {
    const getEventIcon = (type) => {
        switch (type) {
            case 'parlay_update': return TrophyIcon;
            case 'odds_change': return ChartBarIcon;
            case 'system_alert': return BellIcon;
            case 'governance_trigger': return ExclamationTriangleIcon;
            case 'performance_metric': return LightningBoltIcon;
            default: return ClockIcon;
        }
    };

    const EventIcon = getEventIcon(event.event_type);

    return (
        <div className="bg-gray-800/30 border border-gray-700/50 rounded-lg p-4 transition-all hover:bg-gray-700/30">
            <div className="flex items-start justify-between mb-2">
                <div className="flex items-center space-x-2">
                    <EventIcon className="w-5 h-5 text-blue-400" />
                    <span className="font-medium text-white capitalize">
                        {event.event_type?.replace(/_/g, ' ')}
                    </span>
                </div>
                <div className="flex items-center space-x-2">
                    <AlertBadge level={event.alert_level} />
                    <span className="text-xs text-gray-400">
                        {new Date(event.timestamp).toLocaleTimeString()}
                    </span>
                </div>
            </div>

            <div className="text-sm text-gray-300">
                {event.data?.message || (
                    <pre className="text-xs bg-gray-900/50 p-2 rounded overflow-x-auto">
                        {JSON.stringify(event.data, null, 2)}
                    </pre>
                )}
            </div>

            {event.source && (
                <div className="mt-2 text-xs text-gray-500">
                    Source: {event.source}
                </div>
            )}
        </div>
    );
};

// Performance Metrics Chart (simplified)
const MetricsChart = ({ metrics }) => {
    const latestMetrics = metrics.slice(0, 20);

    return (
        <div className="bg-gray-800/50 border border-gray-700 rounded-xl p-6">
            <h3 className="text-xl font-semibold text-white mb-4 flex items-center">
                <ChartBarIcon className="w-6 h-6 mr-2 text-blue-400" />
                Performance Metrics
            </h3>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {latestMetrics.map((metric, index) => (
                    <div key={index} className="bg-gray-900/50 p-4 rounded-lg">
                        <div className="text-sm text-gray-400 mb-1">
                            {metric.metric_name?.replace(/_/g, ' ')}
                        </div>
                        <div className="text-2xl font-bold text-white">
                            {metric.value?.toFixed(1)} <span className="text-sm text-gray-400">{metric.unit}</span>
                        </div>
                        {metric.alert_triggered && (
                            <div className="mt-2">
                                <AlertBadge level="warning" />
                            </div>
                        )}
                    </div>
                ))}
            </div>
        </div>
    );
};

// Parlay Builder Component
const ParlayBuilder = ({ onSubmit }) => {
    const [legs, setLegs] = useState([]);
    const [stake, setStake] = useState(10);

    const addLeg = () => {
        setLegs([...legs, { team: '', odds: 0, type: 'moneyline' }]);
    };

    const updateLeg = (index, field, value) => {
        const newLegs = [...legs];
        newLegs[index][field] = value;
        setLegs(newLegs);
    };

    const removeLeg = (index) => {
        setLegs(legs.filter((_, i) => i !== index));
    };

    const calculateTotalOdds = () => {
        return legs.reduce((total, leg) => {
            const decimal = leg.odds > 0 ? (leg.odds / 100) + 1 : (100 / Math.abs(leg.odds)) + 1;
            return total * decimal;
        }, 1);
    };

    const handleSubmit = () => {
        if (legs.length > 0) {
            onSubmit({ legs, stake, totalOdds: calculateTotalOdds() });
        }
    };

    return (
        <div className="bg-gray-800/50 border border-gray-700 rounded-xl p-6">
            <h3 className="text-xl font-semibold text-white mb-4 flex items-center">
                <TrophyIcon className="w-6 h-6 mr-2 text-yellow-400" />
                Parlay Builder
            </h3>

            <div className="space-y-4">
                {legs.map((leg, index) => (
                    <div key={index} className="flex items-center space-x-2 bg-gray-900/50 p-3 rounded-lg">
                        <input
                            type="text"
                            placeholder="Team/Selection"
                            value={leg.team}
                            onChange={(e) => updateLeg(index, 'team', e.target.value)}
                            className="flex-1 bg-gray-700 text-white px-3 py-2 rounded border border-gray-600 focus:border-blue-500"
                        />
                        <input
                            type="number"
                            placeholder="Odds"
                            value={leg.odds}
                            onChange={(e) => updateLeg(index, 'odds', parseFloat(e.target.value))}
                            className="w-24 bg-gray-700 text-white px-3 py-2 rounded border border-gray-600 focus:border-blue-500"
                        />
                        <button
                            onClick={() => removeLeg(index)}
                            className="text-red-400 hover:text-red-300 px-2 py-1 rounded"
                        >
                            ✕
                        </button>
                    </div>
                ))}

                <div className="flex items-center justify-between">
                    <button
                        onClick={addLeg}
                        className="bg-blue-600 hover:bg-blue-500 text-white px-4 py-2 rounded-lg transition-colors"
                    >
                        + Add Leg
                    </button>

                    <div className="flex items-center space-x-4">
                        <div>
                            <label className="text-gray-400 text-sm">Stake ($)</label>
                            <input
                                type="number"
                                value={stake}
                                onChange={(e) => setStake(parseFloat(e.target.value))}
                                className="w-20 bg-gray-700 text-white px-2 py-1 rounded border border-gray-600 ml-2"
                            />
                        </div>

                        {legs.length > 0 && (
                            <div className="text-right">
                                <div className="text-gray-400 text-sm">Total Odds</div>
                                <div className="text-white font-bold">+{((calculateTotalOdds() - 1) * 100).toFixed(0)}</div>
                                <div className="text-green-400 text-sm">
                                    Payout: ${(stake * calculateTotalOdds()).toFixed(2)}
                                </div>
                            </div>
                        )}
                    </div>
                </div>

                {legs.length > 0 && (
                    <button
                        onClick={handleSubmit}
                        className="w-full bg-green-600 hover:bg-green-500 text-white py-2 rounded-lg transition-colors font-medium"
                    >
                        Place Parlay Bet
                    </button>
                )}
            </div>
        </div>
    );
};

// Main Dashboard Component
const EQ12Dashboard = () => {
    const { connectionStatus, messageHistory, sendMessage } = useWebSocket('ws://localhost:3001/ws?user_id=dashboard_user');

    const [healthData, setHealthData] = useState({});
    const [events, setEvents] = useState([]);
    const [metrics, setMetrics] = useState([]);
    const [activeTab, setActiveTab] = useState('overview');

    // Process WebSocket messages
    useEffect(() => {
        if (messageHistory.length > 0) {
            const latestMessage = messageHistory[0];

            if (latestMessage.event_type === 'health_status') {
                setHealthData(latestMessage.data);
            }

            if (latestMessage.event_type === 'performance_metric') {
                setMetrics(prev => [latestMessage.data.metric, ...prev.slice(0, 49)]);
            }

            setEvents(messageHistory);
        }
    }, [messageHistory]);

    const handleParlaySubmit = (parlayData) => {
        sendMessage({
            type: 'user_action',
            action: {
                type: 'parlay_created',
                data: parlayData
            },
            user_id: 'dashboard_user'
        });
    };

    const tabs = [
        { id: 'overview', name: 'Overview', icon: ChartBarIcon },
        { id: 'health', name: 'Health', icon: CheckCircleIcon },
        { id: 'events', name: 'Events', icon: BellIcon },
        { id: 'parlay', name: 'Parlay Builder', icon: TrophyIcon },
    ];

    return (
        <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900">
            {/* Header */}
            <header className="bg-gray-800/50 backdrop-blur-sm border-b border-gray-700">
                <div className="max-w-7xl mx-auto px-6 py-4">
                    <div className="flex items-center justify-between">
                        <div>
                            <h1 className="text-3xl font-bold text-white">EQ12 Dashboard</h1>
                            <p className="text-gray-400 mt-1">Real-time betting analytics & governance</p>
                        </div>

                        <div className="flex items-center space-x-4">
                            <ConnectionStatus status={connectionStatus} />
                            <div className="text-gray-400 text-sm">
                                {new Date().toLocaleString()}
                            </div>
                        </div>
                    </div>

                    {/* Navigation Tabs */}
                    <nav className="flex space-x-1 mt-6">
                        {tabs.map((tab) => {
                            const Icon = tab.icon;
                            return (
                                <button
                                    key={tab.id}
                                    onClick={() => setActiveTab(tab.id)}
                                    className={`flex items-center px-4 py-2 rounded-lg font-medium transition-colors ${activeTab === tab.id
                                            ? 'bg-blue-600 text-white'
                                            : 'text-gray-400 hover:text-white hover:bg-gray-700'
                                        }`}
                                >
                                    <Icon className="w-5 h-5 mr-2" />
                                    {tab.name}
                                </button>
                            );
                        })}
                    </nav>
                </div>
            </header>

            {/* Main Content */}
            <main className="max-w-7xl mx-auto px-6 py-8">
                {/* Overview Tab */}
                {activeTab === 'overview' && (
                    <div className="space-y-8">
                        {/* Quick Stats */}
                        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                            <div className="bg-gradient-to-r from-blue-600 to-blue-700 p-6 rounded-xl text-white">
                                <div className="flex items-center justify-between">
                                    <div>
                                        <p className="text-blue-100">Active Connections</p>
                                        <p className="text-2xl font-bold">{healthData.components?.websockets?.details?.active_connections || 0}</p>
                                    </div>
                                    <LightningBoltIcon className="w-8 h-8 text-blue-200" />
                                </div>
                            </div>

                            <div className="bg-gradient-to-r from-green-600 to-green-700 p-6 rounded-xl text-white">
                                <div className="flex items-center justify-between">
                                    <div>
                                        <p className="text-green-100">System Health</p>
                                        <p className="text-2xl font-bold">{healthData.summary?.health_percentage?.toFixed(0) || 0}%</p>
                                    </div>
                                    <CheckCircleIcon className="w-8 h-8 text-green-200" />
                                </div>
                            </div>

                            <div className="bg-gradient-to-r from-yellow-600 to-yellow-700 p-6 rounded-xl text-white">
                                <div className="flex items-center justify-between">
                                    <div>
                                        <p className="text-yellow-100">Events Today</p>
                                        <p className="text-2xl font-bold">{events.length}</p>
                                    </div>
                                    <BellIcon className="w-8 h-8 text-yellow-200" />
                                </div>
                            </div>

                            <div className="bg-gradient-to-r from-purple-600 to-purple-700 p-6 rounded-xl text-white">
                                <div className="flex items-center justify-between">
                                    <div>
                                        <p className="text-purple-100">Active Parlays</p>
                                        <p className="text-2xl font-bold">47</p>
                                    </div>
                                    <TrophyIcon className="w-8 h-8 text-purple-200" />
                                </div>
                            </div>
                        </div>

                        {/* Health Grid and Recent Events */}
                        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                            {/* Health Status */}
                            <div>
                                <h2 className="text-2xl font-bold text-white mb-6">System Health</h2>
                                <div className="grid grid-cols-1 gap-4">
                                    {healthData.components && Object.entries(healthData.components).map(([component, health]) => (
                                        <HealthCard key={component} component={component} health={health} />
                                    ))}
                                </div>
                            </div>

                            {/* Recent Events */}
                            <div>
                                <h2 className="text-2xl font-bold text-white mb-6">Recent Events</h2>
                                <div className="space-y-4 max-h-96 overflow-y-auto">
                                    {events.slice(0, 10).map((event, index) => (
                                        <EventCard key={event.event_id || index} event={event} />
                                    ))}
                                </div>
                            </div>
                        </div>

                        {/* Performance Metrics */}
                        <MetricsChart metrics={metrics} />
                    </div>
                )}

                {/* Health Tab */}
                {activeTab === 'health' && (
                    <div className="space-y-8">
                        <h2 className="text-2xl font-bold text-white">System Health Monitoring</h2>

                        {healthData.summary && (
                            <div className="bg-gray-800/50 border border-gray-700 rounded-xl p-6">
                                <h3 className="text-xl font-semibold text-white mb-4">Overall Health Summary</h3>
                                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                    <div className="text-center">
                                        <div className="text-3xl font-bold text-green-400">{healthData.summary.health_percentage?.toFixed(1)}%</div>
                                        <div className="text-gray-400">Overall Health</div>
                                    </div>
                                    <div className="text-center">
                                        <div className="text-3xl font-bold text-blue-400">{healthData.summary.healthy_components}</div>
                                        <div className="text-gray-400">Healthy Components</div>
                                    </div>
                                    <div className="text-center">
                                        <div className="text-3xl font-bold text-gray-400">{healthData.summary.total_components}</div>
                                        <div className="text-gray-400">Total Components</div>
                                    </div>
                                </div>
                            </div>
                        )}

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            {healthData.components && Object.entries(healthData.components).map(([component, health]) => (
                                <HealthCard key={component} component={component} health={health} />
                            ))}
                        </div>
                    </div>
                )}

                {/* Events Tab */}
                {activeTab === 'events' && (
                    <div className="space-y-6">
                        <h2 className="text-2xl font-bold text-white">Real-time Events</h2>

                        <div className="grid grid-cols-1 gap-4">
                            {events.map((event, index) => (
                                <EventCard key={event.event_id || index} event={event} />
                            ))}
                        </div>
                    </div>
                )}

                {/* Parlay Builder Tab */}
                {activeTab === 'parlay' && (
                    <div className="space-y-6">
                        <h2 className="text-2xl font-bold text-white">Parlay Builder</h2>
                        <ParlayBuilder onSubmit={handleParlaySubmit} />
                    </div>
                )}
            </main>
        </div>
    );
};

export default EQ12Dashboard;
