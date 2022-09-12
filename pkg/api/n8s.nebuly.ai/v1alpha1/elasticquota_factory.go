package v1alpha1

import (
	v1 "k8s.io/api/core/v1"
	"k8s.io/apimachinery/pkg/api/resource"
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
)

type eqBuilder struct {
	ElasticQuota
}

func (e *eqBuilder) WithMin(min v1.ResourceList) *eqBuilder {
	e.ElasticQuota.Spec.Min = min
	return e
}

func (e *eqBuilder) WithMax(max v1.ResourceList) *eqBuilder {
	e.ElasticQuota.Spec.Max = max
	return e
}

func (e *eqBuilder) WithMinGPUMemory(gpuMemory int64) *eqBuilder {
	if e.ElasticQuota.Spec.Min == nil {
		e.ElasticQuota.Spec.Min = make(v1.ResourceList)
	}
	e.ElasticQuota.Spec.Min[ResourceGPUMemory] = *resource.NewQuantity(gpuMemory, resource.DecimalSI)
	return e
}

func (e *eqBuilder) WithMaxGPUMemory(gpuMemory int64) *eqBuilder {
	if e.ElasticQuota.Spec.Max == nil {
		e.ElasticQuota.Spec.Max = make(v1.ResourceList)
	}
	e.ElasticQuota.Spec.Max[ResourceGPUMemory] = *resource.NewQuantity(gpuMemory, resource.DecimalSI)
	return e
}

func (e *eqBuilder) WithMinCPUMilli(cpuMilli int64) *eqBuilder {
	if e.ElasticQuota.Spec.Min == nil {
		e.ElasticQuota.Spec.Min = make(v1.ResourceList)
	}
	e.ElasticQuota.Spec.Min[v1.ResourceCPU] = *resource.NewMilliQuantity(cpuMilli, resource.DecimalSI)
	return e
}

func (e *eqBuilder) WithMaxCPUMilli(cpuMilli int64) *eqBuilder {
	if e.ElasticQuota.Spec.Max == nil {
		e.ElasticQuota.Spec.Max = make(v1.ResourceList)
	}
	e.ElasticQuota.Spec.Max[v1.ResourceCPU] = *resource.NewMilliQuantity(cpuMilli, resource.DecimalSI)
	return e
}

func (e *eqBuilder) Get() ElasticQuota {
	return e.ElasticQuota
}

func BuildEq(namespace, name string) *eqBuilder {
	eq := ElasticQuota{
		TypeMeta: metav1.TypeMeta{
			Kind:       "ElasticQuota",
			APIVersion: GroupVersion.String(),
		},
		ObjectMeta: metav1.ObjectMeta{
			Name:      name,
			Namespace: namespace,
		},
	}
	return &eqBuilder{eq}
}