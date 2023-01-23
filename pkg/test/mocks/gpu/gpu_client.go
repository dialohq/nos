/*
 * Copyright 2023 nebuly.com.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

// Code generated by mockery v2.15.0. DO NOT EDIT.

package gpu

import (
	context "context"

	gpu "github.com/nebuly-ai/nos/pkg/gpu"
	mock "github.com/stretchr/testify/mock"
)

// Client is an autogenerated mock type for the Client type
type Client struct {
	mock.Mock
}

// GetAllocatableDevices provides a mock function with given fields: ctx
func (_m *Client) GetAllocatableDevices(ctx context.Context) (gpu.DeviceList, gpu.Error) {
	ret := _m.Called(ctx)

	var r0 gpu.DeviceList
	if rf, ok := ret.Get(0).(func(context.Context) gpu.DeviceList); ok {
		r0 = rf(ctx)
	} else {
		if ret.Get(0) != nil {
			r0 = ret.Get(0).(gpu.DeviceList)
		}
	}

	var r1 gpu.Error
	if rf, ok := ret.Get(1).(func(context.Context) gpu.Error); ok {
		r1 = rf(ctx)
	} else {
		if ret.Get(1) != nil {
			r1 = ret.Get(1).(gpu.Error)
		}
	}

	return r0, r1
}

// GetDevices provides a mock function with given fields: ctx
func (_m *Client) GetDevices(ctx context.Context) (gpu.DeviceList, gpu.Error) {
	ret := _m.Called(ctx)

	var r0 gpu.DeviceList
	if rf, ok := ret.Get(0).(func(context.Context) gpu.DeviceList); ok {
		r0 = rf(ctx)
	} else {
		if ret.Get(0) != nil {
			r0 = ret.Get(0).(gpu.DeviceList)
		}
	}

	var r1 gpu.Error
	if rf, ok := ret.Get(1).(func(context.Context) gpu.Error); ok {
		r1 = rf(ctx)
	} else {
		if ret.Get(1) != nil {
			r1 = ret.Get(1).(gpu.Error)
		}
	}

	return r0, r1
}

// GetUsedDevices provides a mock function with given fields: ctx
func (_m *Client) GetUsedDevices(ctx context.Context) (gpu.DeviceList, gpu.Error) {
	ret := _m.Called(ctx)

	var r0 gpu.DeviceList
	if rf, ok := ret.Get(0).(func(context.Context) gpu.DeviceList); ok {
		r0 = rf(ctx)
	} else {
		if ret.Get(0) != nil {
			r0 = ret.Get(0).(gpu.DeviceList)
		}
	}

	var r1 gpu.Error
	if rf, ok := ret.Get(1).(func(context.Context) gpu.Error); ok {
		r1 = rf(ctx)
	} else {
		if ret.Get(1) != nil {
			r1 = ret.Get(1).(gpu.Error)
		}
	}

	return r0, r1
}

type mockConstructorTestingTNewClient interface {
	mock.TestingT
	Cleanup(func())
}

// NewClient creates a new instance of Client. It also registers a testing interface on the mock and a cleanup function to assert the mocks expectations.
func NewClient(t mockConstructorTestingTNewClient) *Client {
	mock := &Client{}
	mock.Mock.Test(t)

	t.Cleanup(func() { mock.AssertExpectations(t) })

	return mock
}
