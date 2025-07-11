import os
from opentelemetry import trace, metrics
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.system_metrics import SystemMetricsInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
import threading
import time
import psutil


def setup_signoz_monitoring(app):
    """
    SignOz 모니터링 설정을 초기화합니다.
    """
    # 환경 변수에서 설정 가져오기 (기본값 제공)
    signoz_endpoint = os.getenv("SIGNOZ_ENDPOINT", "https://collector.kakaotech.com")
    service_name = os.getenv("SERVICE_NAME", "ai-server")
    
    # OpenTelemetry 리소스 설정
    resource = Resource.create({"service.name": service_name})
    
    # Tracer Provider 설정
    trace_provider = TracerProvider(resource=resource)
    
    # SignOz Collector로 스팬 전송
    otlp_trace_exporter = OTLPSpanExporter(
        endpoint=f"{signoz_endpoint}/v1/traces",
        headers={}
    )
    
    # Batch Span Processor 추가
    trace_provider.add_span_processor(BatchSpanProcessor(otlp_trace_exporter))
    
    # Tracer Provider 설정
    trace.set_tracer_provider(trace_provider)
    
    # Meter Provider 설정 (메트릭용)
    otlp_metric_exporter = OTLPMetricExporter(
        endpoint=f"{signoz_endpoint}/v1/metrics",
        headers={}
    )
    
    # 주기적 메트릭 내보내기 (30초마다)
    metric_reader = PeriodicExportingMetricReader(
        exporter=otlp_metric_exporter,
        export_interval_millis=30000
    )
    
    meter_provider = MeterProvider(
        resource=resource,
        metric_readers=[metric_reader]
    )
    
    # Meter Provider 설정
    metrics.set_meter_provider(meter_provider)
    
    # FastAPI OpenTelemetry Instrumentation
    FastAPIInstrumentor.instrument_app(app)
    
    # Requests OpenTelemetry Instrumentation
    RequestsInstrumentor().instrument()
    
    # 시스템 메트릭 수집 (CPU, 메모리, 디스크 등)
    SystemMetricsInstrumentor().instrument()
    
    # psutil 기반 시스템 메트릭 수집
    PsutilInstrumentor().instrument()
    
    print(f"SignOz 모니터링이 설정되었습니다. 서비스: {service_name}, 엔드포인트: {signoz_endpoint}")
    print("추적(Traces)과 메트릭(Metrics) 수집이 활성화되었습니다.")


def get_meter(name="ai-server"):
    """
    메트릭을 기록하기 위한 Meter 인스턴스를 반환합니다.
    """
    return metrics.get_meter(name)


def record_api_request(endpoint: str, method: str, status_code: int, duration_ms: float):
    """
    API 요청 메트릭을 기록합니다.
    """
    meter = get_meter()
    
    # 요청 수 카운터
    request_counter = meter.create_counter(
        name="api_requests_total",
        description="Total number of API requests"
    )
    request_counter.add(1, {"endpoint": endpoint, "method": method, "status_code": str(status_code)})
    
    # 응답 시간 히스토그램
    response_time_histogram = meter.create_histogram(
        name="api_response_time_ms",
        description="API response time in milliseconds"
    )
    response_time_histogram.record(duration_ms, {"endpoint": endpoint, "method": method})


def record_chat_request(user_id: str, model: str, duration_ms: float):
    """
    채팅 요청 메트릭을 기록합니다.
    """
    meter = get_meter()
    
    # 채팅 요청 수 카운터
    chat_counter = meter.create_counter(
        name="chat_requests_total",
        description="Total number of chat requests"
    )
    chat_counter.add(1, {"user_id": user_id, "model": model})
    
    # 채팅 응답 시간 히스토그램
    chat_response_time = meter.create_histogram(
        name="chat_response_time_ms",
        description="Chat response time in milliseconds"
    )
    chat_response_time.record(duration_ms, {"model": model})


def record_vector_search(duration_ms: float, result_count: int):
    """
    벡터 검색 메트릭을 기록합니다.
    """
    meter = get_meter()
    
    # 벡터 검색 수 카운터
    search_counter = meter.create_counter(
        name="vector_searches_total",
        description="Total number of vector searches"
    )
    search_counter.add(1)
    
    # 검색 응답 시간 히스토그램
    search_time = meter.create_histogram(
        name="vector_search_time_ms",
        description="Vector search time in milliseconds"
    )
    search_time.record(duration_ms)
    
    # 검색 결과 수 히스토그램
    result_count_histogram = meter.create_histogram(
        name="vector_search_results_count",
        description="Number of results from vector search"
    )
    result_count_histogram.record(result_count) 


def record_system_metrics(interval_sec: int = 30):
    """
    psutil을 이용해 주기적으로 시스템(CPU/메모리) 메트릭을 기록합니다.
    interval_sec: 측정 주기(초)
    """
    meter = get_meter()
    cpu_gauge = meter.create_observable_gauge(
        name="system_cpu_percent",
        callbacks=[lambda options: [metrics.Observation(psutil.cpu_percent(), {})]],
        description="System CPU usage percent"
    )
    mem_gauge = meter.create_observable_gauge(
        name="system_memory_percent",
        callbacks=[lambda options: [metrics.Observation(psutil.virtual_memory().percent, {})]],
        description="System memory usage percent"
    )
    # 별도 스레드에서 주기적으로 값을 기록 (콜백 기반이므로 실제로는 OpenTelemetry가 pull)
    # 필요시 추가적인 커스텀 메트릭도 이곳에서 구현 가능
    print(f"시스템 메트릭 기록 활성화 (주기: {interval_sec}초)")

# FastAPI 실행 시 한 번만 호출되도록 main.py에서 setup_signoz_monitoring 이후 호출 필요 